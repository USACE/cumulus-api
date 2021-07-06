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
		`select 
		key,
		bucket,
		dss_datatype,
		dss_cpart,
		dss_dpart,
		dss_epart,
		dss_fpart,
		dss_unit
		from v_download_request vdr 
		where download_id = $1
		and date_part('year', forecast_version) != '1111'
		and forecast_version in (
			select distinct forecast_version 
			from v_download_request d
			where d.download_id = vdr.download_id 
			and d.product_id = vdr.product_id 
			and d.forecast_version between vdr.datetime_start and vdr.datetime_end 
			order by d.forecast_version desc limit 2)
		UNION
		select 
		key,
		bucket,
		dss_datatype,
		dss_cpart,
		dss_dpart,
		dss_epart,
		dss_fpart,
		dss_unit
		from v_download_request vdr where vdr.download_id = $1
		and date_part('year', forecast_version) = '1111'
		order by dss_fpart, key`,
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
