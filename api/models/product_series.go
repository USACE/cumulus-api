package models

import (
	"context"
	"fmt"

	// Postgres Database Driver
	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	_ "github.com/jackc/pgx/v4"
	"github.com/jackc/pgx/v4/pgxpool"
)

// ProductSeriesInfo is required data for creating a product series
type ProductSeriesInfo struct {
	Name          string     `json:"name"`
	DssFpart      string     `json:"dss_fpart" db:"dss_fpart"`
	DssDatatypeID *uuid.UUID `json:"dss_datatype_id,omitempty" db:"dss_datatype_id"`
	DssDatatype   string     `json:"dss_datatype" db:"dss_datatype"`
	ParameterID   uuid.UUID  `json:"parameter_id" db:"parameter_id"`
	Parameter     string     `json:"parameter"`
	UnitID        uuid.UUID  `json:"unit_id" db:"unit_id"`
	Unit          string     `json:"unit"`
	Description   string     `json:"description"`
	SuiteID       uuid.UUID  `json:"suite_id" db:"suite_id"`
	Suite         string     `json:"suite"`
	Label         string     `json:"label"`
}

// ProductSeriesTemporal is temporal data from a series' products
type ProductSeriesTemporal struct {
	TemporalResolution *int `json:"temporal_resolution" db:"temporal_resolution"`
	TemporalDuration   *int `json:"temporal_duration" db:"temporal_duration"`
}

type ProductSeries struct {
	ProductIdentifiers
	Tags []uuid.UUID `json:"tags" db:"tags"`
	ProductSeriesInfo
	ProductSeriesTemporal
	CoverageSummary
}

var listProductSeriesSQL = `SELECT id, slug, name, label, tags, temporal_resolution, temporal_duration,
								parameter_id, parameter, unit_id, unit, dss_fpart, dss_datatype_id, 
								dss_datatype, description, suite_id, suite, after, before, 
								productfile_count, last_forecast_version
							FROM v_product_series`

// ListProducts returns a list of products
func ListProductSeries(db *pgxpool.Pool) ([]ProductSeries, error) {
	pp := make([]ProductSeries, 0)
	if err := pgxscan.Select(context.Background(), db, &pp, listProductSeriesSQL); err != nil {
		return make([]ProductSeries, 0), err
	}
	return pp, nil
}

// GetProductSeries returns a single product series
func GetProductSeries(db *pgxpool.Pool, productID *uuid.UUID) (*ProductSeries, error) {
	var p ProductSeries
	if err := pgxscan.Get(context.Background(), db, &p, listProductSeriesSQL+" WHERE id = $1", productID); err != nil {
		return nil, err
	}
	return &p, nil
}

// GetProductSeriesAvailability returns Availability for a product series
func GetProductSeriesAvailability(db *pgxpool.Pool, ID *uuid.UUID) (*Availability, error) {
	// https://stackoverflow.com/questions/29023336/generate-series-in-postgres-from-start-and-end-date-in-a-table
	a := Availability{ProductID: *ID, DateCounts: make([]DateCount, 0)}
	if err := pgxscan.Select(
		context.Background(), db, &a.DateCounts,
		`SELECT series.day                           AS date,
				COALESCE(SUM(daily_counts.count), 0) AS count
		FROM (
			SELECT generate_series(MIN(pf.datetime)::date, MAX(pf.datetime)::date, '1 Day') AS day
			FROM productfile pf
			JOIN product p ON pf.product_id = p.id
			WHERE p.product_series_id = $1
		) series
		LEFT OUTER JOIN (
			SELECT datetime::date as day,
				   COUNT(*)       as count
			FROM productfile pf
			JOIN product p ON pf.product_id = p.id
			WHERE p.product_series_id = $1
			GROUP BY day
		) daily_counts ON daily_counts.day = series.day
		GROUP BY series.day
		ORDER BY series.day`, ID,
	); err != nil {
		return nil, err
	}
	return &a, nil
}

// GetProductSeriesIngestStatus
func GetProductSeriesIngestStatus(db *pgxpool.Pool) ([]ProductStatus, error) {
	ps := make([]ProductStatus, 0)
	productStatusSql := `SELECT 
		pser.slug AS slug,
		MAX(ps.latest_product_datetime) AS latest_product_datetime,
		MIN(ps.acceptable_timedelta)::text AS acceptable_timedelta,
		MIN(ps.actual_timedelta)::text AS actual_timedelta,
		BOOL_AND(ps.is_current) AS is_current
	FROM v_product_status ps
	JOIN product p ON ps.slug = p.slug
	JOIN product_series pser ON p.product_series_id = pser.id
	GROUP BY pser.slug`
	if err := pgxscan.Select(context.Background(), db, &ps, productStatusSql); err != nil {
		return make([]ProductStatus, 0), err
	}
	return ps, nil
}

// GetProductSeriesSlugs
func GetProductSeriesSlugs(db *pgxpool.Pool) (map[string]uuid.UUID, error) {
	pp := make([]ProductIdentifiers, 0)
	if err := pgxscan.Select(
		context.Background(), db, &pp, `SELECT id, slug FROM v_product_series`,
	); err != nil {
		return make(map[string]uuid.UUID), err
	}
	// convert array to map
	m := make(map[string]uuid.UUID)
	for _, p := range pp {
		m[p.Slug] = p.ID
	}
	return m, nil
}

// CreateProductSeries creates a single product series
func CreateProductSeries(db *pgxpool.Pool, p *ProductSeriesInfo) (*ProductSeries, error) {

	// Helper Function to Build Slug
	// Slug First Pass is: <Suite Name> <Label || ""> <ParameterName>
	nameFirstPass := func() (string, error) {

		sql := fmt.Sprintf(
			`SELECT s.name || ' ' || '%s' || ' ' || p.name AS str
			 FROM parameter p
			 CROSS JOIN (SELECT name FROM suite where id = $2) s
			 WHERE p.id = $1`, p.Label,
		)

		var s struct {
			Str string
		}
		if err := pgxscan.Get(context.Background(), db, &s, sql, p.ParameterID, p.SuiteID); err != nil {
			return "", err
		}
		return s.Str, nil
	}

	// Get Concatenated Name to Use As Input for Slug (First Pass)
	s, err := nameFirstPass()
	if err != nil {
		return nil, err
	}

	// Assign Slug Based on Product Name; Slug Must Be Table Unique
	slug, err := NextUniqueSlug(db, "product_series", "slug", s, "", "")
	if err != nil {
		return nil, err
	}

	// Insert Into Database Using New Slug
	var pID uuid.UUID
	if err := pgxscan.Get(
		context.Background(), db, &pID,
		`INSERT INTO product_series (dss_fpart, dss_datatype_id, parameter_id, unit_id, description, suite_id, label, slug) VALUES
			($1, $2, $3, $4, $5, $6, $7, $8)
		RETURNING id`, p.DssFpart, p.DssDatatypeID, p.ParameterID, p.UnitID, p.Description, p.SuiteID, p.Label, slug,
	); err != nil {
		return nil, err
	}
	return GetProductSeries(db, &pID)
}

// UpdateProductSeries updates a single product series
func UpdateProductSeries(db *pgxpool.Pool, p *ProductSeries) (*ProductSeries, error) {
	var pID uuid.UUID
	if err := pgxscan.Get(
		context.Background(), db, &pID,
		`UPDATE product_series SET dss_fpart=$2, dss_datatype_id=$3,
		                    	   parameter_id=$4, unit_id=$5, description=$6, suite_id=$7, label=$8
		 WHERE id = $1
		 RETURNING id`, p.ID, p.DssFpart, p.DssDatatypeID, p.ParameterID, p.UnitID, p.Description, p.SuiteID, p.Label,
	); err != nil {
		return nil, err
	}
	return GetProductSeries(db, &pID)
}

// DeleteProductSeries deletes a single product series
func DeleteProductSeries(db *pgxpool.Pool, pID *uuid.UUID) error {
	if _, err := db.Exec(context.Background(), `UPDATE product_series SET deleted=true WHERE id=$1`, pID); err != nil {
		return err
	}
	return nil
}

// UndeleteProduct undeletes a single product series
func UndeleteProductSeries(db *pgxpool.Pool, pID *uuid.UUID) (*ProductSeries, error) {
	if _, err := db.Exec(context.Background(), `UPDATE product_series SET deleted=false WHERE id=$1`, pID); err != nil {
		return nil, err
	}
	return GetProductSeries(db, pID)
}

func TagProductSeries(db *pgxpool.Pool, productID *uuid.UUID, tagID *uuid.UUID) (*ProductSeries, error) {
	if _, err := db.Exec(
		context.Background(),
		`INSERT INTO product_tags (product_series_id, tag_id) VALUES ($1, $2)
		 ON CONFLICT ON CONSTRAINT unique_tag_product_series DO NOTHING`,
		productID, tagID,
	); err != nil {
		return nil, err
	}
	return GetProductSeries(db, productID)
}

func UntagProductSeries(db *pgxpool.Pool, productID *uuid.UUID, tagID *uuid.UUID) (*ProductSeries, error) {
	if _, err := db.Exec(
		context.Background(), `DELETE FROM product_tags WHERE product_series_id=$1 AND tag_id=$2`, productID, tagID,
	); err != nil {
		return nil, err
	}
	return GetProductSeries(db, productID)
}
