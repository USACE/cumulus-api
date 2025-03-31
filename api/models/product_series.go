package models

import (
	"context"

	// Postgres Database Driver
	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	_ "github.com/jackc/pgx/v4"
	"github.com/jackc/pgx/v4/pgxpool"
)

// ProductSeriesInfo holds information required to create a product series
type ProductSeriesInfo struct {
	Name               string     `json:"name"`
	TemporalResolution *int       `json:"temporal_resolution" db:"temporal_resolution"`
	TemporalDuration   *int       `json:"temporal_duration" db:"temporal_duration"`
	DssFpart           string     `json:"dss_fpart" db:"dss_fpart"`
	DssDatatypeID      *uuid.UUID `json:"dss_datatype_id,omitempty" db:"dss_datatype_id"`
	DssDatatype        string     `json:"dss_datatype" db:"dss_datatype"`
	ParameterID        uuid.UUID  `json:"parameter_id" db:"parameter_id"`
	Parameter          string     `json:"parameter"`
	UnitID             uuid.UUID  `json:"unit_id" db:"unit_id"`
	Unit               string     `json:"unit"`
	Description        string     `json:"description"`
	SuiteID            uuid.UUID  `json:"suite_id" db:"suite_id"`
	Suite              string     `json:"suite"`
	Label              string     `json:"label"`
}

type ProductSeries struct {
	ProductIdentifiers
	Tags []uuid.UUID `json:"tags" db:"tags"`
	ProductSeriesInfo
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
