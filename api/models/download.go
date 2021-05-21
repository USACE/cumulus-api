package models

import (
	"api/config"
	"context"
	"fmt"
	"time"

	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v4/pgxpool"
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
	ProfileID     *uuid.UUID  `json:"profile_id" db:"profile_id"`
	DatetimeStart time.Time   `json:"datetime_start" db:"datetime_start"`
	DatetimeEnd   time.Time   `json:"datetime_end" db:"datetime_end"`
	WatershedID   uuid.UUID   `json:"watershed_id" db:"watershed_id"`
	ProductID     []uuid.UUID `json:"product_id" db:"product_id"`
}

// Download holds all information about a download
type Download struct {
	ID uuid.UUID `json:"id"`
	DownloadRequest
	DownloadStatus
	PackagerInfo
	// Include Watershed Name and Watershed Slug for Convenience
	WatershedSlug string `json:"watershed_slug" db:"watershed_slug"`
	WatershedName string `json:"watershed_name" db:"watershed_name"`
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
	DownloadID uuid.UUID             `json:"download_id"`
	OutputKey  string                `json:"output_key"`
	Watershed  Watershed             `json:"watershed"`
	Contents   []PackagerContentItem `json:"contents"`
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
	   processing_start, processing_end, status_id, watershed_id, watershed_slug, watershed_name, status, product_id
	   FROM v_download
	`, cfg.StaticHost,
)

// ListDownloads returns all downloads from the database
func ListDownloads(db *pgxpool.Pool) ([]Download, error) {
	dd := make([]Download, 0)
	if err := pgxscan.Select(context.Background(), db, &dd, listDownloadsSQL); err != nil {
		return make([]Download, 0), err
	}
	return dd, nil
}

// ListMyDownloads returns all downloads for a given ProfileID
func ListMyDownloads(db *pgxpool.Pool, profileID *uuid.UUID) ([]Download, error) {
	dd := make([]Download, 0)
	if err := pgxscan.Select(context.Background(), db, &dd, listDownloadsSQL+" WHERE profile_id = $1", profileID); err != nil {
		return make([]Download, 0), err
	}
	return dd, nil
}

// GetDownload returns a single download record
func GetDownload(db *pgxpool.Pool, downloadID *uuid.UUID) (*Download, error) {
	var d Download
	if err := pgxscan.Get(context.Background(), db, &d, listDownloadsSQL+" WHERE id = $1", downloadID); err != nil {
		return nil, err
	}
	return &d, nil
}

// GetDownloadPackagerRequest retrieves the information packager needs to package a download
func GetDownloadPackagerRequest(db *pgxpool.Pool, downloadID *uuid.UUID) (*PackagerRequest, error) {

	pr := PackagerRequest{
		DownloadID: *downloadID,
		OutputKey:  fmt.Sprintf("cumulus/download/dss/download_%s.dss", downloadID),
		Contents:   make([]PackagerContentItem, 0),
	}

	if err = pgxscan.Select(
		context.Background(), db, &pr.Contents,
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
			   CASE WHEN dss_datatype = 'INST-VAL' AND date_part('hour', datetime_dss_dpart) = 0 AND date_part('minute', datetime_dss_dpart) = 0
	               	THEN to_char(datetime_dss_dpart - interval '1 Day', 'DDMONYYYY:24MI')
	               	ELSE COALESCE(to_char(datetime_dss_dpart, 'DDMONYYYY:HH24MI'), '') END as dss_dpart,
			   CASE WHEN date_part('hour', datetime_dss_epart) = 0 AND date_part('minute', datetime_dss_dpart) = 0
	               	THEN to_char(datetime_dss_epart - interval '1 Day', 'DDMONYYYY:24MI')
	               	ELSE COALESCE(to_char(datetime_dss_epart, 'DDMONYYYY:HH24MI'), '') END as dss_epart,
			   dss_fpart,
			   dss_unit
		FROM (
			SELECT f.file as key,
			(SELECT config_value from config where config_name = 'write_to_bucket') AS bucket,
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

	// Attach Watershed
	w, err := GetDownloadWatershed(db, downloadID)
	if err != nil {
		return nil, err
	}
	pr.Watershed = *w

	return &pr, nil
}

// CreateDownload creates a download record in
func CreateDownload(db *pgxpool.Pool, dr *DownloadRequest) (*Download, error) {

	// TRANSACTION
	//////////////
	tx, err := db.Begin(context.Background())
	if err != nil {
		return nil, err
	}
	defer tx.Rollback(context.Background())

	// Insert Record of Download
	rows, err := tx.Query(
		context.Background(),
		`INSERT INTO download (datetime_start, datetime_end, status_id, watershed_id, profile_id)
		 VALUES ($1, $2, '94727878-7a50-41f8-99eb-a80eb82f737a', $3, $4)
		 RETURNING id`, dr.DatetimeStart, dr.DatetimeEnd, dr.WatershedID, dr.ProfileID,
	)
	if err != nil {
		tx.Rollback(context.Background())
		return nil, err
	}
	var dID uuid.UUID
	if err := pgxscan.ScanOne(&dID, rows); err != nil {
		tx.Rollback(context.Background())
		return nil, err
	}
	// Insert Record for Each Product Associated with Download
	for _, pID := range dr.ProductID {
		if _, err := tx.Exec(
			context.Background(),
			`INSERT INTO download_product (product_id, download_id) VALUES ($1, $2)`,
			pID, dID,
		); err != nil {
			tx.Rollback(context.Background())
			return nil, err
		}
	}
	if err := tx.Commit(context.Background()); err != nil {
		return nil, err
	}

	return GetDownload(db, &dID)
}

// UpdateDownload is called by Packager to update progress
func UpdateDownload(db *pgxpool.Pool, downloadID *uuid.UUID, info *PackagerInfo) (*Download, error) {

	UpdateProgress := func() error {
		sql := `UPDATE download SET progress = $2 WHERE id = $1`
		if _, err := db.Exec(context.Background(), sql, downloadID, info.Progress); err != nil {
			return err
		}
		return nil
	}

	UpdateProgressSetComplete := func() error {
		sql := `UPDATE download set progress = $2, processing_end = $3 WHERE id = $1`
		if _, err := db.Exec(context.Background(), sql, downloadID, info.Progress); err != nil {
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
