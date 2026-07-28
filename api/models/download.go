package models

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"path"
	"strings"
	"time"

	"github.com/USACE/cumulus-api/api/config"

	"github.com/georgysavva/scany/v2/pgxscan"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
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
// Supports both watershed-based and custom GeoJSON region-based downloads
type DownloadRequest struct {
	Sub            *uuid.UUID  `json:"sub" db:"sub"`
	DatetimeStart  time.Time   `json:"datetime_start" db:"datetime_start"`
	DatetimeEnd    time.Time   `json:"datetime_end" db:"datetime_end"`
	WatershedID    *uuid.UUID  `json:"watershed_id,omitempty" db:"watershed_id"`
	ProductID      []uuid.UUID `json:"product_id" db:"product_id"`
	Format         *string     `json:"format" db:"format"`
	ClipGeoJSON    *string     `json:"clip_geojson,omitempty" db:"clip_geojson"` // GeoJSON string from database
	ClipRegionName *string     `json:"clip_region_name,omitempty" db:"clip_region_name"`
}

// Download holds all information about a download
type Download struct {
	ID uuid.UUID `json:"id"`
	DownloadRequest
	DownloadStatus
	PackagerInfo
	// Include Watershed Name and Watershed Slug for Convenience
	WatershedSlug *string   `json:"watershed_slug,omitempty" db:"watershed_slug"`
	WatershedName *string   `json:"watershed_name,omitempty" db:"watershed_name"`
	ClipBbox      []float64 `json:"clip_bbox,omitempty" db:"clip_bbox"`
	ClipName      string    `json:"clip_name,omitempty" db:"clip_name"`
	// RawFile is the untouched S3 key (not exposed to clients); File is derived
	// from it as a file-serving URL by attachFileLink(s).
	RawFile         *string    `json:"-" db:"raw_file"`
	RetrievalCount  int64      `json:"retrieval_count" db:"retrieval_count"`
	LastRetrievedAt *time.Time `json:"last_retrieved_at,omitempty" db:"last_retrieved_at"`
}

// PackagerInfo holds all information Packager provides after a download starts
type PackagerInfo struct {
	Progress        int16      `json:"progress"`
	File            *string    `json:"file"`
	StatusID        uuid.UUID  `json:"status_id"`
	ProcessingStart time.Time  `json:"processing_start" db:"processing_start"`
	ProcessingEnd   *time.Time `json:"processing_end" db:"processing_end"`
	Manifest        *JSONB     `json:"manifest"`
	SizeBytes       *int64     `json:"size_bytes,omitempty" db:"size_bytes"`
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
	Srid float64   `json:"srid"`
}

// PackagerContentItem is a single item for Packager to include in output file
// Note: Previously called DownloadContentItem
type PackagerContentItem struct {
	ProductID   string `json:"product_id" db:"product_id"`
	Bucket      string `json:"bucket"`
	Key         string `json:"key"`
	DssDatatype string `json:"dss_datatype" db:"dss_datatype"`
	DssFpart    string `json:"dss_fpart" db:"dss_fpart"`
	DssCpart    string `json:"dss_cpart" db:"dss_cpart"`
	DssDpart    string `json:"dss_dpart" db:"dss_dpart"`
	DssEpart    string `json:"dss_epart" db:"dss_epart"`
	DssUnit     string `json:"dss_unit" db:"dss_unit"`
}

var listDownloadsSQL = `SELECT id, sub, datetime_start, datetime_end, progress, raw_file,
	   processing_start, processing_end, status_id, watershed_id, watershed_slug, watershed_name,
	   status, product_id, format, manifest, clip_geojson, clip_region_name, clip_bbox, clip_name,
	   size_bytes, retrieval_count, last_retrieved_at
	   FROM v_download
	`

// downloadLinkLifetime is how long after the packager finishes that a download's
// file stays fetchable. Expiry is measured from processing_end, not from when
// the link was handed out, so a link is NOT renewable: re-requesting the
// download returns the same URL with the same deadline. Past it the user
// re-requests the package, which is cheap relative to keeping every historical
// package reachable forever.
const downloadLinkLifetime = 48 * time.Hour

// attachFileLink replaces d.File (if a completed file exists) with the URL of
// the file-serving endpoint. d.RawFile, the actual S3 key, is left untouched for
// server-side use (see ServeDownloadFile).
//
// The package filename is the last path segment rather than a query parameter
// because clients derive the local filename from the URL path: browsers fall
// back to it when Content-Disposition carries no filename, and HEC-RTS splits
// the path itself (CumulusManagerGridDao.getStagingFilePath). A URL ending in
// "/file" made both write a name-less "file" instead of "download_<id>.dss".
//
// There is deliberately no signature. Expiry is a property of the download row,
// which ServeDownloadFile reads anyway, and the link is derived entirely from
// the download id -- which the caller must already hold to get here. An HMAC
// over values the server owns, issued to anyone who asks, would prove nothing
// the id does not.
func attachFileLink(d *Download) {
	if d == nil || d.RawFile == nil {
		return
	}
	url := fmt.Sprintf("%s/downloads/%s/file/%s", cfg.StaticHost, d.ID, path.Base(*d.RawFile))
	d.File = &url
}

func attachFileLinks(dd []Download) {
	for i := range dd {
		attachFileLink(&dd[i])
	}
}

// FileLinkExpired reports whether the download's package has aged past
// downloadLinkLifetime and should no longer be served. A download with no
// processing_end never completed, so it has nothing to serve either.
func (d *Download) FileLinkExpired() bool {
	if d.ProcessingEnd == nil {
		return true
	}
	return time.Since(*d.ProcessingEnd) > downloadLinkLifetime
}

// ListDownloads returns all downloads from the database
func ListDownloads(db *pgxpool.Pool) ([]Download, error) {
	dd := make([]Download, 0)
	if err := pgxscan.Select(context.Background(), db, &dd, listDownloadsSQL); err != nil {
		return make([]Download, 0), err
	}
	attachFileLinks(dd)
	return dd, nil
}

// ListMyDownloads returns all downloads for a given Sub
func ListMyDownloads(db *pgxpool.Pool, sub *uuid.UUID) ([]Download, error) {
	dd := make([]Download, 0)
	if err := pgxscan.Select(context.Background(), db, &dd, listDownloadsSQL+" WHERE sub = $1", sub); err != nil {
		return make([]Download, 0), err
	}
	attachFileLinks(dd)
	return dd, nil
}

// ListAdminDownloads returns downloads for admin
func ListAdminDownloads(db *pgxpool.Pool) ([]Download, error) {
	dd := make([]Download, 0)
	if err := pgxscan.Select(context.Background(), db, &dd, listDownloadsSQL+" ORDER BY processing_start DESC LIMIT 50"); err != nil {
		return make([]Download, 0), err
	}
	attachFileLinks(dd)
	return dd, nil
}

// GetDownload returns a single download record
func GetDownload(db *pgxpool.Pool, downloadID *uuid.UUID) (*Download, error) {
	var d Download
	if err := pgxscan.Get(context.Background(), db, &d, listDownloadsSQL+" WHERE id = $1", downloadID); err != nil {
		return nil, err
	}
	attachFileLink(&d)
	return &d, nil
}

// packagerRequestTimeout bounds the packager payload query. It reads v_download_request, which
// scans productfile; without a deadline a slow plan pins one of the pool's connections until the
// client's TCP session dies, and the pool is only 15 wide. Failing fast surfaces the problem as a
// 500 the packager logs instead of a silent stall.
const packagerRequestTimeout = 45 * time.Second

// GetDownloadPackagerRequest retrieves the information packager needs to package a download
// Beware of [NULL] (https://stackoverflow.com/questions/37922340/why-postgresql-json-agg-function-does-not-return-an-empty-array)
func GetDownloadPackagerRequest(ctx context.Context, db *pgxpool.Pool, downloadID *uuid.UUID) (*PackagerRequest, error) {

	pr := PackagerRequest{
		Contents: make([]PackagerContentItem, 0),
	}

	ctx, cancel := context.WithTimeout(ctx, packagerRequestTimeout)
	defer cancel()

	// 'req' is the download's slice of v_download_request, evaluated ONCE and reused by both
	// branches below. This previously re-expanded the view inside a correlated IN (...) subquery,
	// which -- because it was correlated AND carried a LIMIT -- the planner could not flatten into a
	// semi-join, so it re-scanned productfile once per candidate row.
	//
	// 'forecast' reproduces that subquery's "latest 2 issue cycles per product" with a window
	// function over the single scan. dense_rank (not row_number) is what matches the original
	// SELECT DISTINCT ... ORDER BY forecast_version DESC LIMIT 2: two distinct *versions*, all rows
	// belonging to each. The original correlated the range bound on r.datetime_start/r.datetime_end
	// as well as r.product_id, but those two come from the download record and so are constant for a
	// given download_id -- product_id was the only real partition key.
	if err := pgxscan.Get(
		ctx, db, &pr,
		`WITH req AS MATERIALIZED (
			SELECT * FROM v_download_request WHERE download_id = $1
		),
		forecast AS (
			SELECT r.*,
			       dense_rank() OVER (
			           PARTITION BY r.product_id
			           ORDER BY r.forecast_version DESC
			       ) AS vrank
			FROM req r
			WHERE r.forecast_version >= '1900-01-01'::timestamptz
			    AND r.forecast_version BETWEEN r.datetime_start - interval '24 hours' AND r.datetime_end
		),
		download_contents AS (
			SELECT download_id,
			       product_id,
			       key,
		           bucket,
			       dss_datatype,
			       dss_cpart,
			       dss_dpart,
			       dss_epart,
			       dss_fpart,
			       dss_unit
		    FROM forecast
		    WHERE vrank <= 2
		    -- UNION ALL, not UNION: the two branches are disjoint by construction (non-sentinel
		    -- vs sentinel version), so deduplicating across them only buys a sort.
		    UNION ALL
		    SELECT download_id,
			       product_id,
			       key,
		           bucket,
		           dss_datatype,
		           dss_cpart,
		           dss_dpart,
		           dss_epart,
		           dss_fpart,
		           dss_unit
		    FROM req
		    -- Sentinel test as a range, not equality: there are multiple distinct year-1111
		    -- sentinel values in production. See the note in R__05_views_downloads.sql.
		    WHERE forecast_version < '1900-01-01'::timestamptz
		)
		SELECT d.id AS download_id,
		       json_build_object(
				   'name', CASE 
				       WHEN d.clip_geojson IS NOT NULL THEN COALESCE(d.clip_region_name, 'Custom Region')
				       ELSE w.name 
				   END,
				   'bbox', CASE
				       WHEN d.clip_geojson IS NOT NULL THEN ARRAY[
					       ST_XMin(ST_Transform(ST_GeomFromGeoJSON(d.clip_geojson), COALESCE(w.output_srid, 5070))),
					       ST_YMin(ST_Transform(ST_GeomFromGeoJSON(d.clip_geojson), COALESCE(w.output_srid, 5070))),
					       ST_XMax(ST_Transform(ST_GeomFromGeoJSON(d.clip_geojson), COALESCE(w.output_srid, 5070))),
					       ST_YMax(ST_Transform(ST_GeomFromGeoJSON(d.clip_geojson), COALESCE(w.output_srid, 5070)))
					   ]
				       ELSE ARRAY[
					       ST_XMin(ST_Transform(w.geometry,w.output_srid)),
					       ST_YMin(ST_Transform(w.geometry,w.output_srid)),
					       ST_XMax(ST_Transform(w.geometry,w.output_srid)),
					       ST_YMax(ST_Transform(w.geometry,w.output_srid))
					   ]
				   END,
				   'srid', COALESCE(w.output_srid, 5070)
			   ) AS extent,
			   CONCAT(
				   'cumulus/download/', f.abbreviation,
				   '/download_', d.id, '.', f.extension
				) AS output_key,
			   f.abbreviation AS format,
			   COALESCE(c.contents, '[]'::jsonb) AS contents
		FROM download d
		INNER JOIN download_format f ON f.id = d.download_format_id
		LEFT JOIN watershed w ON w.id = d.watershed_id
		LEFT JOIN (
			SELECT download_id,
			       -- ORDER BY belongs on the aggregate: it used to sit on the download_contents CTE,
			       -- where aggregate input order is not guaranteed to survive.
			       jsonb_agg(
					   jsonb_build_object(
						   'product_id',   product_id,
						   'key',          key,
						   'bucket',       bucket,
						   'dss_datatype', dss_datatype,
						   'dss_cpart',    dss_cpart,
						   'dss_dpart',    dss_dpart,
						   'dss_epart',    dss_epart,
						   'dss_fpart',    dss_fpart,
						   'dss_unit',     dss_unit
					   )
					   ORDER BY dss_fpart, key
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
// ident carries the requesting user's display-name claims and may be nil
// (application-key or anonymous requests). When present it refreshes that
// user's user_directory row, which is the only thing admin usage reporting
// needs a directory entry for -- see UpsertUserDirectory.
func CreateDownload(db *pgxpool.Pool, dr *DownloadRequest, ident *UserIdentity) (*Download, error) {

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
		`INSERT INTO download (download_format_id, datetime_start, datetime_end, status_id, watershed_id, sub, clip_geojson, clip_region_name)
		 VALUES (
			 (SELECT id FROM download_format WHERE UPPER(abbreviation) = UPPER($1)), $2, $3,
			 (SELECT id FROM download_status WHERE UPPER(name) = 'INITIATED'), $4, $5, $6, $7
		 )
		 RETURNING id`, dr.Format, dr.DatetimeStart, dr.DatetimeEnd, dr.WatershedID, dr.Sub, dr.ClipGeoJSON, dr.ClipRegionName,
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
	// Refresh this user's display name. Wrapped in a savepoint (pgx implements a
	// nested Begin as SAVEPOINT) so that a failure here -- most plausibly missing
	// grants on user_directory, which is why R__10_grants_user_directory.sql
	// exists -- degrades to a stale display name instead of failing the user's
	// download.
	if dr.Sub != nil && !ident.IsEmpty() {
		if sp, spErr := tx.Begin(context.Background()); spErr != nil {
			log.Printf("user_directory savepoint failed for sub %s: %v", *dr.Sub, spErr)
		} else if err := UpsertUserDirectory(context.Background(), sp, *dr.Sub, ident); err != nil {
			log.Printf("user_directory upsert failed for sub %s: %v", *dr.Sub, err)
			sp.Rollback(context.Background())
		} else if err := sp.Commit(context.Background()); err != nil {
			log.Printf("user_directory savepoint commit failed for sub %s: %v", *dr.Sub, err)
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
		sizeBytes := info.SizeBytes
		if sizeBytes == nil && info.Manifest != nil {
			if v, ok := (*info.Manifest)["size_bytes"].(float64); ok {
				sb := int64(v)
				sizeBytes = &sb
			}
		}
		sql := `UPDATE download set progress = $2, file = $3, processing_end = CURRENT_TIMESTAMP, manifest = $4, size_bytes = $5 WHERE id = $1`
		if _, err := db.Exec(context.Background(), sql, downloadID, info.Progress, info.File, info.Manifest, sizeBytes); err != nil {
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

// IncrementDownloadRetrieval records a single fetch of a download's completed file.
func IncrementDownloadRetrieval(db *pgxpool.Pool, downloadID *uuid.UUID) error {
	_, err := db.Exec(context.Background(),
		`UPDATE download SET retrieval_count = retrieval_count + 1, last_retrieved_at = now() WHERE id = $1`,
		downloadID,
	)
	return err
}

// DownloadUsage is one row of the admin usage report: per-user aggregate
// download activity, joined against the display-name cache when available.
type DownloadUsage struct {
	Sub               uuid.UUID  `json:"sub" db:"sub"`
	DisplayName       string     `json:"display_name" db:"display_name"`
	PreferredUsername *string    `json:"preferred_username" db:"preferred_username"`
	Email             *string    `json:"email" db:"email"`
	RequestCount      int64      `json:"request_count" db:"request_count"`
	RetrievalCount    int64      `json:"retrieval_count" db:"retrieval_count"`
	// TotalBytesPackaged is the size of every package produced for this user
	// (sum of size_bytes), regardless of whether it was ever downloaded.
	TotalBytesPackaged int64 `json:"total_bytes_packaged" db:"total_bytes_packaged"`
	// TotalBytesDownloaded is bytes actually transferred to the user
	// (sum of size_bytes * retrieval_count).
	TotalBytesDownloaded int64      `json:"total_bytes_downloaded" db:"total_bytes_downloaded"`
	LastDownloadAt       *time.Time `json:"last_download_at" db:"last_download_at"`
}

// DownloadUsageFilter controls sorting, text search, and time-range filtering
// for ListDownloadUsage.
type DownloadUsageFilter struct {
	Sort   string // "downloaded"/"gb" (default), "packaged", "requests", or "retrievals"
	Order  string // "asc" or "desc" (default)
	Q      string // substring match against username/email/name/sub
	After  *time.Time
	Before *time.Time
	Limit  int
}

// completedDownloadStatuses are the only statuses counted as real usage --
// FAILED produced nothing, and INITIATED means Packager never finished (or
// never started), so neither represents an actual download.
var completedDownloadStatuses = []string{"SUCCESS", "PARTIAL SUCCESS"}

// ListDownloadUsage returns per-user download usage aggregates for the admin
// usage report, aggregated from the raw download table (not v_download, which
// fans out one row per product per download and would inflate the counts).
func ListDownloadUsage(db *pgxpool.Pool, f DownloadUsageFilter) ([]DownloadUsage, error) {
	sortCol := "total_bytes_downloaded"
	switch f.Sort {
	case "requests":
		sortCol = "request_count"
	case "retrievals":
		sortCol = "retrieval_count"
	case "packaged":
		sortCol = "total_bytes_packaged"
	case "downloaded", "gb":
		sortCol = "total_bytes_downloaded"
	}
	order := "DESC"
	if strings.EqualFold(f.Order, "asc") {
		order = "ASC"
	}

	sql := fmt.Sprintf(`
		SELECT
			d.sub,
			COALESCE(ud.preferred_username, ud.email, ud.name, d.sub::text) AS display_name,
			ud.preferred_username, ud.email,
			COUNT(*) AS request_count,
			COALESCE(SUM(d.retrieval_count), 0)::bigint AS retrieval_count,
			-- Bytes produced (all packages) vs bytes actually transferred (a
			-- package fetched N times moved N * its size; never-fetched = 0).
			-- ::bigint because SUM over BIGINT returns numeric; cast for a clean int64 scan.
			COALESCE(SUM(d.size_bytes), 0)::bigint AS total_bytes_packaged,
			COALESCE(SUM(d.size_bytes * d.retrieval_count), 0)::bigint AS total_bytes_downloaded,
			MAX(d.processing_start) AS last_download_at
		FROM download d
		JOIN download_status s ON s.id = d.status_id
		LEFT JOIN user_directory ud ON ud.sub = d.sub
		WHERE s.name = ANY($5)
		  AND ($1::timestamptz IS NULL OR d.processing_start >= $1)
		  AND ($2::timestamptz IS NULL OR d.processing_start <= $2)
		  AND ($3::text IS NULL OR d.sub::text ILIKE '%%' || $3 || '%%'
		       OR ud.preferred_username ILIKE '%%' || $3 || '%%'
		       OR ud.email ILIKE '%%' || $3 || '%%' OR ud.name ILIKE '%%' || $3 || '%%')
		GROUP BY d.sub, ud.preferred_username, ud.email, ud.name
		ORDER BY %s %s
		LIMIT $4`, sortCol, order)

	var q *string
	if f.Q != "" {
		q = &f.Q
	}

	uu := make([]DownloadUsage, 0)
	if err := pgxscan.Select(context.Background(), db, &uu, sql, f.After, f.Before, q, f.Limit, completedDownloadStatuses); err != nil {
		return make([]DownloadUsage, 0), err
	}
	return uu, nil
}

// ProductUsage is one row of the admin "top products downloaded" report,
// aggregated across all users (user-agnostic).
type ProductUsage struct {
	ProductID      uuid.UUID  `json:"product_id" db:"product_id"`
	ProductName    string     `json:"product_name" db:"product_name"`
	ProductSlug    string     `json:"product_slug" db:"product_slug"`
	RequestCount   int64      `json:"request_count" db:"request_count"`
	LastDownloadAt *time.Time `json:"last_download_at" db:"last_download_at"`
}

// ProductUsageFilter controls sort order, text search, and time-range
// filtering for ListProductUsage. There is deliberately no size/GB metric:
// a single download can bundle multiple products into one package, and
// Packager only reports total package size, not a per-product breakdown, so
// per-product bytes can't be attributed accurately. Only request_count
// (how many download jobs included the product) is meaningful today.
type ProductUsageFilter struct {
	Order  string // "asc" or "desc" (default)
	Q      string // substring match against product name/slug
	After  *time.Time
	Before *time.Time
	Limit  int
}

// ListProductUsage returns the most-downloaded products, independent of which
// users downloaded them. Counts download jobs that included the product
// (via download_product), regardless of how many other products shared that
// same package.
func ListProductUsage(db *pgxpool.Pool, f ProductUsageFilter) ([]ProductUsage, error) {
	order := "DESC"
	if strings.EqualFold(f.Order, "asc") {
		order = "ASC"
	}

	sql := fmt.Sprintf(`
		SELECT
			p.id AS product_id,
			p.name AS product_name,
			p.slug AS product_slug,
			COUNT(*) AS request_count,
			MAX(d.processing_start) AS last_download_at
		FROM download d
		JOIN download_status s ON s.id = d.status_id
		JOIN download_product dp ON dp.download_id = d.id
		JOIN v_product p ON p.id = dp.product_id
		WHERE s.name = ANY($5)
		  AND ($1::timestamptz IS NULL OR d.processing_start >= $1)
		  AND ($2::timestamptz IS NULL OR d.processing_start <= $2)
		  AND ($3::text IS NULL OR p.name ILIKE '%%' || $3 || '%%' OR p.slug ILIKE '%%' || $3 || '%%')
		GROUP BY p.id, p.name, p.slug
		ORDER BY request_count %s
		LIMIT $4`, order)

	var q *string
	if f.Q != "" {
		q = &f.Q
	}

	pp := make([]ProductUsage, 0)
	if err := pgxscan.Select(context.Background(), db, &pp, sql, f.After, f.Before, q, f.Limit, completedDownloadStatuses); err != nil {
		return make([]ProductUsage, 0), err
	}
	return pp, nil
}

// UsageFilter is the shared filter for the admin analytics endpoints
// (GetUsageSummary / GetUsageTimeseries). Every field is optional: an empty
// slice or nil time means "no constraint on this dimension". Within a single
// dimension the values are OR'd (any of these users); across dimensions they
// are AND'd (this user AND this product). Extents match against the coalesced
// clip name -- a watershed name or a custom region name.
type UsageFilter struct {
	Users    []uuid.UUID
	Products []uuid.UUID
	Extents  []string
	After    *time.Time
	Before   *time.Time
	// Limit caps each breakdown to its top-N rows (by request_count) plus a
	// single aggregated "Other" row. <= 0 means uncapped (return every row) --
	// used by the CSV export. The breakdown charts send the default so a
	// deployment with thousands of users doesn't ship thousands of rows per
	// request when only the top few are plotted.
	Limit int
}

// DefaultSummaryLimit is the per-breakdown top-N used when no limit is given.
// Chosen to match the categorical chart palette (8 hues) + an "Other" slot.
const DefaultSummaryLimit = 8

// UsageTotals is the filtered grand total across the whole download set.
type UsageTotals struct {
	RequestCount    int64 `json:"request_count"`
	RetrievalCount  int64 `json:"retrieval_count"`
	BytesDownloaded int64 `json:"bytes_downloaded"`
	BytesPackaged   int64 `json:"bytes_packaged"`
}

// UsageBreakdown is one row of a per-dimension breakdown (a product, an extent,
// or a user). Name is the display label; the "Other" bucket uses name "Other".
type UsageBreakdown struct {
	Name            string `json:"name"`
	RequestCount    int64  `json:"request_count"`
	RetrievalCount  int64  `json:"retrieval_count"`
	BytesDownloaded int64  `json:"bytes_downloaded"`
}

// UsageSummary is the analytics summary response: filtered totals plus the
// three breakdowns, each already capped to top-N + "Other" (unless uncapped).
type UsageSummary struct {
	Totals    UsageTotals      `json:"totals"`
	ByUser    []UsageBreakdown `json:"by_user"`
	ByProduct []UsageBreakdown `json:"by_product"`
	ByExtent  []UsageBreakdown `json:"by_extent"`
}

// capBreakdown keeps the first `limit` rows (already ordered by request_count
// DESC in SQL) and folds the remainder into a single "Other" row, summing each
// metric. limit <= 0 returns rows unchanged. This is what keeps the response
// small: the tail is aggregated server-side rather than shipped row by row.
func capBreakdown(rows []UsageBreakdown, limit int) []UsageBreakdown {
	// Return as-is when there's at most one row past the cap: folding a single
	// tail row into "Other" saves no payload and just hides its name.
	if limit <= 0 || len(rows) <= limit+1 {
		return rows
	}
	other := UsageBreakdown{Name: "Other"}
	for _, r := range rows[limit:] {
		other.RequestCount += r.RequestCount
		other.RetrievalCount += r.RetrievalCount
		other.BytesDownloaded += r.BytesDownloaded
	}
	return append(rows[:limit:limit], other)
}

// nilIfEmptyUUIDs / nilIfEmptyStrings return a typed nil for empty slices so
// the query binds SQL NULL (skipping the filter) instead of an empty array,
// which would make `col = ANY('{}')` match nothing and hide every row.
func nilIfEmptyUUIDs(s []uuid.UUID) interface{} {
	if len(s) == 0 {
		return nil
	}
	return s
}

func nilIfEmptyStrings(s []string) interface{} {
	if len(s) == 0 {
		return nil
	}
	return s
}

// usageFilterCTE is the common `filtered` CTE both analytics queries build on:
// the set of completed downloads matching the filter, one row per download,
// with the extent name resolved without touching v_download's geometry work.
// Bind order: $1 after, $2 before, $3 users, $4 products, $5 extents,
// $6 statuses.
const usageFilterCTE = `
	WITH filtered AS (
		SELECT
			d.id, d.sub, d.size_bytes, d.retrieval_count, d.processing_start,
			CASE
				WHEN d.clip_geojson IS NOT NULL THEN COALESCE(d.clip_region_name, 'Custom Region')
				ELSE w.name
			END AS extent
		FROM download d
		JOIN download_status s ON s.id = d.status_id
		LEFT JOIN watershed w ON w.id = d.watershed_id
		WHERE s.name = ANY($6)
		  AND ($1::timestamptz IS NULL OR d.processing_start >= $1)
		  AND ($2::timestamptz IS NULL OR d.processing_start <= $2)
		  AND ($3::uuid[] IS NULL OR d.sub = ANY($3))
		  AND ($5::text[] IS NULL OR (CASE
				WHEN d.clip_geojson IS NOT NULL THEN COALESCE(d.clip_region_name, 'Custom Region')
				ELSE w.name END) = ANY($5))
		  AND ($4::uuid[] IS NULL OR EXISTS (
				SELECT 1 FROM download_product dp
				WHERE dp.download_id = d.id AND dp.product_id = ANY($4)))
	)`

// GetUsageSummary returns the totals plus per-product, per-extent, and
// per-user breakdowns for the filtered download set, as a single JSON object:
//
//	{ totals: {...}, by_product: [...], by_extent: [...], by_user: [...] }
//
// bytes_downloaded is size_bytes * retrieval_count (bytes actually
// transferred); bytes_packaged is size_bytes (bytes produced). Product
// bytes are per-package, not per-product -- a package's full size is
// attributed to every product it contains, since Packager reports only a
// total (see ProductUsageFilter).
func GetUsageSummary(db *pgxpool.Pool, f UsageFilter) (*UsageSummary, error) {
	sql := usageFilterCTE + `
	SELECT json_build_object(
		'totals', (
			SELECT json_build_object(
				'request_count',    COUNT(*),
				'retrieval_count',  COALESCE(SUM(retrieval_count), 0),
				'bytes_downloaded', COALESCE(SUM(size_bytes * retrieval_count), 0),
				'bytes_packaged',   COALESCE(SUM(size_bytes), 0)
			) FROM filtered
		),
		'by_product', COALESCE((
			SELECT json_agg(r) FROM (
				SELECT
					p.id   AS product_id,
					p.name AS name,
					COUNT(*) AS request_count,
					COALESCE(SUM(f.retrieval_count), 0)                  AS retrieval_count,
					COALESCE(SUM(f.size_bytes * f.retrieval_count), 0)   AS bytes_downloaded
				FROM filtered f
				JOIN download_product dp ON dp.download_id = f.id
				JOIN v_product p ON p.id = dp.product_id
				GROUP BY p.id, p.name
				ORDER BY request_count DESC
			) r
		), '[]'::json),
		'by_extent', COALESCE((
			SELECT json_agg(r) FROM (
				SELECT
					COALESCE(extent, 'Unknown') AS name,
					COUNT(*) AS request_count,
					COALESCE(SUM(retrieval_count), 0)                AS retrieval_count,
					COALESCE(SUM(size_bytes * retrieval_count), 0)   AS bytes_downloaded
				FROM filtered
				GROUP BY extent
				ORDER BY request_count DESC
			) r
		), '[]'::json),
		'by_user', COALESCE((
			SELECT json_agg(r) FROM (
				SELECT
					f.sub AS sub,
					COALESCE(ud.preferred_username, ud.email, ud.name, f.sub::text) AS name,
					COUNT(*) AS request_count,
					COALESCE(SUM(f.retrieval_count), 0)                AS retrieval_count,
					COALESCE(SUM(f.size_bytes * f.retrieval_count), 0) AS bytes_downloaded
				FROM filtered f
				LEFT JOIN user_directory ud ON ud.sub = f.sub
				GROUP BY f.sub, ud.preferred_username, ud.email, ud.name
				ORDER BY request_count DESC
			) r
		), '[]'::json)
	)`

	// Postgres does the grouping and ordering; the tail-folding cap is done in
	// Go (see capBreakdown) since it's simpler than window functions here and
	// the DB->API row count isn't the concern -- the browser payload is.
	var j []byte
	if err := pgxscan.Get(
		context.Background(), db, &j, sql,
		f.After, f.Before, nilIfEmptyUUIDs(f.Users), nilIfEmptyUUIDs(f.Products),
		nilIfEmptyStrings(f.Extents), completedDownloadStatuses,
	); err != nil {
		return nil, err
	}

	var summary UsageSummary
	if err := json.Unmarshal(j, &summary); err != nil {
		return nil, err
	}
	summary.ByUser = capBreakdown(summary.ByUser, f.Limit)
	summary.ByProduct = capBreakdown(summary.ByProduct, f.Limit)
	summary.ByExtent = capBreakdown(summary.ByExtent, f.Limit)
	return &summary, nil
}

// GetUsageTimeseries returns request volume bucketed over time for the
// filtered set, gap-filled so empty buckets come back as zero. interval is
// "day", "week", or "month".
//
// Only request_count and bytes_packaged are reported, both keyed on
// processing_start (the download's creation time) and therefore accurate to
// the bucket. Retrievals/bytes_downloaded are deliberately absent: the schema
// stores a retrieval counter and only the last-fetched timestamp, so fetches
// can't be bucketed by when they happened. A per-fetch download_retrieval
// event table would be required to add a true downloads-over-time series.
func GetUsageTimeseries(db *pgxpool.Pool, f UsageFilter, interval string) ([]UsageTimeseriesPoint, error) {
	// Whitelist the interval -- it is interpolated into the SQL (date_trunc and
	// the generate_series step can't be bound as parameters), so it must never
	// come from raw client input.
	unit := "day"
	switch interval {
	case "week":
		unit = "week"
	case "month":
		unit = "month"
	case "day", "":
		unit = "day"
	default:
		return nil, fmt.Errorf("invalid interval")
	}

	sql := fmt.Sprintf(usageFilterCTE+`,
	bounds AS (
		SELECT
			date_trunc('%[1]s', COALESCE($1::timestamptz, MIN(processing_start))) AS lo,
			date_trunc('%[1]s', COALESCE($2::timestamptz, MAX(processing_start))) AS hi
		FROM filtered
	),
	buckets AS (
		SELECT generate_series(lo, hi, interval '1 %[1]s') AS bucket
		FROM bounds
		WHERE lo IS NOT NULL AND hi IS NOT NULL
	),
	agg AS (
		SELECT
			date_trunc('%[1]s', processing_start) AS bucket,
			COUNT(*) AS request_count,
			COALESCE(SUM(size_bytes), 0)::bigint AS bytes_packaged
		FROM filtered
		GROUP BY 1
	)
	SELECT
		b.bucket AS bucket,
		COALESCE(a.request_count, 0)  AS request_count,
		COALESCE(a.bytes_packaged, 0) AS bytes_packaged
	FROM buckets b
	LEFT JOIN agg a ON a.bucket = b.bucket
	ORDER BY b.bucket`, unit)

	pts := make([]UsageTimeseriesPoint, 0)
	if err := pgxscan.Select(
		context.Background(), db, &pts, sql,
		f.After, f.Before, nilIfEmptyUUIDs(f.Users), nilIfEmptyUUIDs(f.Products),
		nilIfEmptyStrings(f.Extents), completedDownloadStatuses,
	); err != nil {
		return make([]UsageTimeseriesPoint, 0), err
	}
	return pts, nil
}

// UsageTimeseriesPoint is one time bucket of the analytics timeline.
type UsageTimeseriesPoint struct {
	Bucket        time.Time `json:"bucket" db:"bucket"`
	RequestCount  int64     `json:"request_count" db:"request_count"`
	BytesPackaged int64     `json:"bytes_packaged" db:"bytes_packaged"`
}

// UsageUser is one entry for the analytics user selector: a downloading user
// with a display name resolved from the directory cache.
type UsageUser struct {
	Sub         uuid.UUID `json:"sub" db:"sub"`
	DisplayName string    `json:"display_name" db:"display_name"`
}

// ListUsageUsers returns the distinct users who have completed downloads, for
// populating the analytics user filter. Ordered by display name.
func ListUsageUsers(db *pgxpool.Pool) ([]UsageUser, error) {
	sql := `
		SELECT DISTINCT
			d.sub,
			COALESCE(ud.preferred_username, ud.email, ud.name, d.sub::text) AS display_name
		FROM download d
		JOIN download_status s ON s.id = d.status_id
		LEFT JOIN user_directory ud ON ud.sub = d.sub
		WHERE s.name = ANY($1)
		ORDER BY display_name`

	uu := make([]UsageUser, 0)
	if err := pgxscan.Select(context.Background(), db, &uu, sql, completedDownloadStatuses); err != nil {
		return make([]UsageUser, 0), err
	}
	return uu, nil
}
