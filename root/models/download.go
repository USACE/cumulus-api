package models

import (
	"api/root/config"
	"fmt"
	"time"

	"github.com/USACE/go-simple-asyncer/asyncer"

	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	"github.com/lib/pq"
)

// Environment Variable Config
var cfg, err = config.GetConfig()

// if err != nil {
// 	log.Fatal(err.Error())
// }

// DownloadStatus is a domain
type DownloadStatus struct {
	StatusID uuid.UUID `json:"status_id" db:"status_id"`
	Status   string    `json:"status"`
}

// DownloadRequest holds all information from a download request coming from a user
type DownloadRequest struct {
	DatetimeStart time.Time   `json:"datetime_start" db:"datetime_start"`
	DatetimeEnd   time.Time   `json:"datetime_end" db:"datetime_end"`
	BasinID       uuid.UUID   `json:"basin_id" db:"basin_id"`
	ProductID     []uuid.UUID `json:"product_id" db:"product_id"`
}

// Download holds all information about a download
type Download struct {
	ID uuid.UUID `json:"id"`
	DownloadRequest
	DownloadStatus
	PackagerInfo
}

// PackagerInfo holds all information Packager provides after a download starts
type PackagerInfo struct {
	Progress        int16      `json:"progress"`
	File            *string    `json:"file"`
	ProcessingStart time.Time  `json:"processing_start" db:"processing_start"`
	ProcessingEnd   *time.Time `json:"processing_end" db:"processing_end"`
}

// PackagerRequest holds all information sent to Packager necessary to package files
type PackagerRequest struct {
	DownloadID   uuid.UUID             `json:"download_id"`
	OutputBucket string                `json:"output_bucket"`
	OutputKey    string                `json:"output_key"`
	Basin        Basin                 `json:"basin"`
	Contents     []PackagerContentItem `json:"contents"`
}

// PackagerContentItem is a single item for Packager to include in output file
// Note: Previously called DownloadContentItem
type PackagerContentItem struct {
	Bucket      string `json:"bucket"`
	Key         string `json:"key"`
	DssDatatype string `json:"dss_datatype" db:"dss_datatype"`
	DssFpart    string `json:"dss_fpart" db:"dss_fpart"`
	DssCpart    string `json:"dss_cpart" db:"dss_cpart"`
	DssDpart    string `json:"dss_dpart" db:"dss_dpart"`
	DssEpart    string `json:"dss_epart" db:"dss_epart"`
	DssUnit     string `json:"dss_unit" db:"dss_unit"`
}

var listDownloadsSQL = fmt.Sprintf(
	`SELECT id, datetime_start, datetime_end, progress, ('%s' || '/' || file) as file,
	   processing_start, processing_end, status_id, basin_id, status, product_id
	   FROM v_download
	`, cfg.StaticHost,
)

// ListDownloads returns all downloads from the database
func ListDownloads(db *sqlx.DB) ([]Download, error) {

	rows, err := db.Queryx(listDownloadsSQL)
	if err != nil {
		return make([]Download, 0), err
	}
	dd, err := DownloadStructFactory(rows)
	if err != nil {
		return make([]Download, 0), err
	}
	return dd, nil

}

// GetDownload returns a single download record
func GetDownload(db *sqlx.DB, id *uuid.UUID) (*Download, error) {

	rows, err := db.Queryx(listDownloadsSQL+" WHERE id = $1", id)
	if err != nil {
		return nil, err
	}
	dd, err := DownloadStructFactory(rows)
	if err != nil {
		return nil, err
	}
	return &dd[0], nil
}

// GetDownloadBasin returns the basin for a downloadID
func GetDownloadBasin(db *sqlx.DB, downloadID *uuid.UUID) (*Basin, error) {
	var b Basin
	if err := db.Get(
		&b,
		`SELECT b.id,
				b.name,
				b.x_min,
				b.y_min,
				b.x_max,
				b.y_max,
				f.symbol AS office_symbol
		FROM   download d
		INNER JOIN basin b ON d.basin_id = b.id
		JOIN office f ON b.office_id = f.id
		WHERE d.ID = $1`,
		downloadID,
	); err != nil {
		return nil, err
	}
	return &b, nil
}

// GetDownloadPackagerRequest retrieves the information packager needs to package a download
func GetDownloadPackagerRequest(db *sqlx.DB, downloadID *uuid.UUID) (*PackagerRequest, error) {

	pr := PackagerRequest{
		DownloadID:   *downloadID,
		OutputBucket: "corpsmap-data",
		OutputKey:    fmt.Sprintf("cumulus/download/dss/download_%s.dss", downloadID),
		Contents:     make([]PackagerContentItem, 0),
	}

	if err = db.Select(
		&pr.Contents,
		`WITH download_products AS (
			SELECT dp.product_id, d.datetime_start, d.datetime_end
			FROM   download d
			JOIN   download_product dp ON dp.download_id = d.id
			WHERE d.id = $1
		)
		SELECT key,
			   bucket,
			   dss_datatype,
			   dss_cpart,
			   CASE WHEN date_part('hour', datetime_dss_dpart) = 0 AND date_part('minute', datetime_dss_dpart) = 0
	               	THEN to_char(datetime_dss_dpart - interval '1 Day', 'DDMONYYYY:24MI')
	               	ELSE COALESCE(to_char(datetime_dss_dpart, 'DDMONYYYY:HH24MI'), '') END as dss_dpart,
			   CASE WHEN date_part('hour', datetime_dss_epart) = 0 AND date_part('minute', datetime_dss_dpart) = 0
	               	THEN to_char(datetime_dss_epart - interval '1 Day', 'DDMONYYYY:24MI')
	               	ELSE COALESCE(to_char(datetime_dss_epart, 'DDMONYYYY:HH24MI'), '') END as dss_epart,
			   dss_fpart,
			   dss_unit
		FROM (
			SELECT f.file as key,
			'corpsmap-data' AS bucket,
			 CASE WHEN p.temporal_duration = 0 THEN 'INST-VAL'
				  ELSE 'PER-CUM'
				  END as dss_datatype,
			 CASE WHEN p.temporal_duration = 0 THEN f.datetime
				  ELSE f.datetime - p.temporal_duration * interval '1 Second'
				  END as datetime_dss_dpart,
			 CASE WHEN p.temporal_duration = 0 THEN null
				  ELSE f.datetime
				  END as datetime_dss_epart,
			 p.dss_fpart as dss_fpart,
			 u.name      as dss_unit,
			 a.name      as dss_cpart
			FROM productfile f
			INNER JOIN download_products dp ON dp.product_id = f.product_id
			INNER JOIN product p on f.product_id = p.id
			INNER JOIN unit u on p.unit_id = u.id
			INNER JOIN parameter a on a.id = p.parameter_id
			WHERE f.datetime >= dp.datetime_start AND f.datetime <= dp.datetime_end
			ORDER BY f.product_id, f.datetime
		) as dss`,
		downloadID,
	); err != nil {
		return nil, err
	}

	// Attach Basin
	b, err := GetDownloadBasin(db, downloadID)
	if err != nil {
		return nil, err
	}
	pr.Basin = *b

	return &pr, nil
}

// CreateDownload creates a download record in
func CreateDownload(db *sqlx.DB, dr *DownloadRequest, ae asyncer.Asyncer) (*Download, error) {

	// Creates a download record and scans into a new struct (with UUID)
	// Pre-Load Download with DownloadRequest
	d := Download{DownloadRequest: *dr}
	createDownloadSQL := `INSERT INTO download (datetime_start, datetime_end, status_id, basin_id)
			              VALUES ($1, $2, '94727878-7a50-41f8-99eb-a80eb82f737a', $3)
			              RETURNING *`
	if err := db.Get(&d, createDownloadSQL, dr.DatetimeStart, dr.DatetimeEnd, dr.BasinID); err != nil {
		return nil, err
	}

	for _, pID := range d.ProductID {
		// TODO: make SQL a prepared statement
		if _, err := db.Exec(
			`INSERT INTO download_product (product_id, download_id) VALUES ($1, $2)`,
			pID, d.ID,
		); err != nil {
			return nil, err
		}
		return &d, nil
	}

	return &d, nil
}

// UpdateDownload is called by Packager to update progress
func UpdateDownload(db *sqlx.DB, downloadID *uuid.UUID, info *PackagerInfo) (*Download, error) {

	UpdateProgress := func() error {
		sql := `UPDATE download SET progress = $2 WHERE id = $1`
		if _, err := db.Exec(sql, downloadID, info.Progress); err != nil {
			return err
		}
		return nil
	}

	UpdateProgressSetComplete := func() error {
		sql := `UPDATE download set progress = $2, processing_end = $3 WHERE id = $1`
		if _, err := db.Exec(sql, downloadID, info.Progress); err != nil {
			return err
		}
		return nil
	}

	if info.Progress == 100 {
		t := time.Now()
		info.ProcessingEnd = &t
		if err := UpdateProgressSetComplete(); err != nil {
			return nil, err
		}
	}
	if err := UpdateProgress(); err != nil {
		return nil, err
	}

	return GetDownload(db, downloadID)
}

// DownloadStructFactory converts download rows to download structs
// Necessary for scanning arrays created from postgres array_agg()
func DownloadStructFactory(rows *sqlx.Rows) ([]Download, error) {
	dd := make([]Download, 0)
	defer rows.Close()
	var d Download
	for rows.Next() {
		err := rows.Scan(
			&d.ID, &d.DatetimeStart, &d.DatetimeEnd, &d.Progress, &d.File,
			&d.ProcessingStart, &d.ProcessingEnd, &d.StatusID, &d.BasinID, &d.Status, pq.Array(&d.ProductID),
		)
		if err != nil {
			return make([]Download, 0), err
		}
		dd = append(dd, d)
	}
	return dd, nil
}
