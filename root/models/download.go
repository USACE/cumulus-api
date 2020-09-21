package models

import (
	"api/root/asyncer"
	"encoding/json"
	"fmt"
	"time"

	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	"github.com/lib/pq"
)

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
	Contents     []PackagerContentItem `json:"contents"`
}

// PackagerContentItem is a single item for Packager to include in output file
// Note: Previously called DownloadContentItem
type PackagerContentItem struct {
	Name     string `json:"name"`
	DssFpart string `json:"dss_fpart" db:"dss_fpart"`
	Bucket   string `json:"bucket"`
	Key      string `json:"key"`
}

var listDownloadsSQL = `SELECT id, datetime_start, datetime_end, progress, file,
							   processing_start, processing_end, status_id, basin_id, status, product_id
					   FROM v_download
					   `

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

// BuildPackagerRequest builds the request for Packager from a fully-populated download
func BuildPackagerRequest(db *sqlx.DB, d *Download) (*PackagerRequest, error) {

	pr := PackagerRequest{
		DownloadID:   d.ID,
		OutputBucket: "corpsmap-data",
		OutputKey:    fmt.Sprintf("cumulus/download/dss/download_%s.dss", d.ID),
		Contents:     make([]PackagerContentItem, 0),
	}

	sql := `SELECT f.file as key,
		           'corpsmap-data' AS bucket,
			       p.name as name,
			       p.dss_fpart as dss_fpart
		    FROM productfile f
		    INNER JOIN product p on f.product_id = p.id
		    WHERE f.datetime >= ? AND f.datetime <= ?
		    AND f.product_id IN (?)
		    order by f.product_id, f.datetime
	`

	// sqlx.In returns queries with the `?` bindvar, we can rebind it for our backend
	query, args, err := sqlx.In(sql, d.DatetimeStart.Format(time.RFC3339), d.DatetimeEnd.Format(time.RFC3339), d.ProductID)
	if err != nil {
		return nil, err
	}
	query = db.Rebind(query)
	if err = db.Select(&pr.Contents, query, args...); err != nil {
		return nil, err
	}
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

	createDownloadProductSQL := `INSERT INTO download_product (product_id, download_id) VALUES ($1, $2)`
	for _, pID := range d.ProductID {
		if _, err := db.Exec(createDownloadProductSQL, pID, d.ID); err != nil {
			return nil, err
		}
	}

	// Create Packager Request from Download
	packagerRequest, err := BuildPackagerRequest(db, &d)
	if err != nil {
		return nil, err
	}
	payload, err := json.Marshal(packagerRequest)
	if err != nil {
		return nil, err
	}

	// Fire Async Call to Packager
	if err := ae.CallAsync("corpsmap-cumulus-packager", payload); err != nil {
		return nil, err
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
