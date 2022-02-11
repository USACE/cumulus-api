package models

import (
	"context"
	"fmt"
	"time"

	"github.com/USACE/cumulus-api/api/config"

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
// TODO; Update DownloadRequest to accept a bbox instead of an explicit WatershedID
// Could choose to leave WatershedID as optional field for metrics tracking by Watershed
type DownloadRequest struct {
	Sub           *uuid.UUID  `json:"sub" db:"sub"`
	DatetimeStart time.Time   `json:"datetime_start" db:"datetime_start"`
	DatetimeEnd   time.Time   `json:"datetime_end" db:"datetime_end"`
	WatershedID   uuid.UUID   `json:"watershed_id" db:"watershed_id"`
	ProductID     []uuid.UUID `json:"product_id" db:"product_id"`
	Format        *string     `json:"format" db:"format"`
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
	StatusID        uuid.UUID  `json:"status_id"`
	ProcessingStart time.Time  `json:"processing_start" db:"processing_start"`
	ProcessingEnd   *time.Time `json:"processing_end" db:"processing_end"`
}

// PackagerRequest holds all information sent to Packager necessary to package files
type PackagerRequest struct {
	DownloadID uuid.UUID             `json:"download_id"`
	OutputKey  string                `json:"output_key"`
	Contents   []PackagerContentItem `json:"contents"`
	Format     string                `json:"format"`
	Extent     Extent                `json:"extent"`
}

// Extent is a name and a bounding box
type Extent struct {
	Name string    `json:"name"`
	Bbox []float64 `json:"bbox"`
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
	`SELECT id, sub, datetime_start, datetime_end, progress, ('%s' || '/' || file) as file,
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

// ListMyDownloads returns all downloads for a given Sub
func ListMyDownloads(db *pgxpool.Pool, sub *uuid.UUID) ([]Download, error) {
	dd := make([]Download, 0)
	if err := pgxscan.Select(context.Background(), db, &dd, listDownloadsSQL+" WHERE sub = $1", sub); err != nil {
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
// Beware of [NULL] (https://stackoverflow.com/questions/37922340/why-postgresql-json-agg-function-does-not-return-an-empty-array)
func GetDownloadPackagerRequest(db *pgxpool.Pool, downloadID *uuid.UUID) (*PackagerRequest, error) {

	pr := PackagerRequest{
		Contents: make([]PackagerContentItem, 0),
	}

	if err = pgxscan.Get(
		context.Background(), db, &pr,
		`WITH download_contents AS (
			SELECT download_id,
			       key,
		           bucket,
			       dss_datatype,
			       dss_cpart,
			       dss_dpart,
			       dss_epart,
			       dss_fpart,
			       dss_unit
		    FROM v_download_request r
		    WHERE download_id = $1
		        AND date_part('year', r.forecast_version) != '1111'
		    	AND r.forecast_version in (
		    		SELECT DISTINCT forecast_version
		    		FROM v_download_request r2
		    		WHERE r2.download_id = $1
					    AND r2.product_id = r.product_id
		    			AND r2.forecast_version BETWEEN r.datetime_start - interval '24 hours' AND r.datetime_end
		    		ORDER BY r2.forecast_version DESC
		    		LIMIT 2
		    	)
		    UNION
		    SELECT download_id,
			       key,
		           bucket,
		           dss_datatype,
		           dss_cpart,
		           dss_dpart,
		           dss_epart,
		           dss_fpart,
		           dss_unit
		    FROM v_download_request
		    WHERE download_id = $1 AND date_part('year', forecast_version) = '1111'
		    ORDER BY dss_fpart, key
		)
		SELECT d.id AS download_id,
		       json_build_object(
				   'name', w.name,
				   'bbox', ARRAY[
					   ST_XMin(w.geometry),ST_Ymin(w.geometry),
					   ST_XMax(w.geometry),ST_YMax(w.geometry)
					]
			   ) AS extent,
			   CONCAT(
				   'cumulus/download/', f.abbreviation,
				   '/download_', d.id, '.', f.extension
				) AS output_key,
			   f.abbreviation AS format,
			   COALESCE(c.contents, '[]'::jsonb) AS contents
		FROM download d
		INNER JOIN download_format f ON f.id = d.download_format_id
		INNER JOIN watershed w ON w.id = d.watershed_id
		LEFT JOIN (
			SELECT download_id,
			       jsonb_agg(
					   jsonb_build_object(
						   'key',          key,
						   'bucket',       bucket,
						   'dss_datatype', dss_datatype,
						   'dss_cpart',    dss_cpart,
						   'dss_dpart',    dss_dpart,
						   'dss_epart',    dss_epart,
						   'dss_fpart',    dss_fpart,
						   'dss_unit',     dss_unit
					   )
				   ) AS contents
			FROM download_contents
			GROUP BY download_id
		) as c ON c.download_id = d.id
		WHERE d.id = $1`, downloadID,
	); err != nil {
		return nil, err
	}

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
		`INSERT INTO download (download_format_id, datetime_start, datetime_end, status_id, watershed_id, sub)
		 VALUES (
			 (SELECT id FROM download_format WHERE UPPER(abbreviation) = UPPER($1)), $2, $3,
			 (SELECT id FROM download_status WHERE UPPER(name) = 'INITIATED'), $4, $5
		 )
		 RETURNING id`, dr.Format, dr.DatetimeStart, dr.DatetimeEnd, dr.WatershedID, dr.Sub,
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
		sql := `UPDATE download SET progress = $2, status_id = $3 WHERE id = $1`
		if _, err := db.Exec(context.Background(), sql, downloadID, info.Progress, info.StatusID); err != nil {
			return err
		}
		return nil
	}

	UpdateProgressSetComplete := func() error {
		sql := `UPDATE download set progress = $2, file = $3, processing_end = CURRENT_TIMESTAMP WHERE id = $1`
		if _, err := db.Exec(context.Background(), sql, downloadID, info.Progress, info.File); err != nil {
			return err
		}
		return nil
	}

	if info.Progress == 100 {

		if err := UpdateProgressSetComplete(); err != nil {
			return nil, err
		}
	}
	if err := UpdateProgress(); err != nil {
		return nil, err
	}

	return GetDownload(db, downloadID)
}

// GetDownloadMetrics returns a various metrics
func GetDownloadMetrics(db *pgxpool.Pool) ([]byte, error) {

	var j []byte
	if err := pgxscan.Get(
		context.Background(), db, &j, ` 
			select json_build_object(
				'count', (select json_build_object(
					'total', (SELECT count(id) from download),
					'days_1', (SELECT count(id) FROM download WHERE processing_start >= NOW() - INTERVAL '24 HOURS'),
					'days_7', (SELECT count(id) FROM download WHERE processing_start >= NOW() - INTERVAL '7 DAYS'),
					'days_30', (SELECT count(id) FROM download WHERE processing_start >= NOW() - INTERVAL '30 DAYS')
				)),
				'top_watersheds', (
						WITH top_watersheds AS (
						SELECT t.cnt as count, t.watershed_name, t.office FROM
						(
							SELECT count(vd.id) AS cnt, watershed_name, o.name as office FROM cumulus.v_download vd
							JOIN cumulus.watershed w ON w.id = vd.watershed_id 
							JOIN cumulus.office o ON o.id = w.office_id 
							GROUP BY watershed_name,o.name
						) AS t
						ORDER BY t.cnt DESC LIMIT 10
						)
						SELECT json_agg(top_watersheds)
							FROM top_watersheds
				),
				'top_products', (
					WITH top_products AS (
						SELECT t.cnt as count, t.name FROM
						(
							SELECT count(d.id) AS cnt, p.name FROM download d 
							JOIN download_product dp ON dp.download_id = d.id
							JOIN v_product p ON p.id = dp.product_id 
							GROUP BY p.name
						) AS t
						ORDER BY t.cnt DESC LIMIT 10
					)
					SELECT json_agg(top_products)
						FROM top_products
				)
			)			
			`,
	); err != nil {
		return nil, err
	}
	return j, nil

	// var d Download
	// if err := pgxscan.Get(context.Background(), db, &d, listDownloadsSQL+" WHERE id = $1", downloadID); err != nil {
	// 	return nil, err
	// }
	// return &d, nil
}
