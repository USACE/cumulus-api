package models

import (
	"strings"
	"time"

	// Postgres Database Driver
	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
)

// Product is a product structure
type Product struct {
	ID                 uuid.UUID  `json:"id"`
	Slug               string     `json:"slug" db:"slug"`
	GroupID            *uuid.UUID `json:"group_id" db:"group_id"`
	Group              *string    `json:"group" db:"group"`
	IsForecast         bool       `json:"is_forecast" db:"is_forecast"`
	IsRealtime         bool       `json:"is_realtime" db:"is_realtime"`
	Name               string     `json:"name"`
	TemporalResolution string     `json:"temporal_resolution" db:"temporal_resolution"`
	TemporalDuration   string     `json:"temporal_duration" db:"temporal_duration"`
	DssFpart           string     `json:"dss_fpart" db:"dss_fpart"`
	Parameter          string     `json:"parameter"`
	Unit               string     `json:"unit"`
	Description        string     `json:"description" db:"description"`
	CoverageSummary
}

// CoverageSummary describes date ranges spanned by a product
// PercentCoverage is a comparison of the number of files on-hand
// with the total number of files that *would* theoretically exist
// in the `after` and `before` date range given a known temporal resolution
// This is easier explained with an example:
// If After: January 1 00:00, 2020 and Before: January 2 00:00, 2020
// Given an hourly product (TemporalResolution 3600 (seconds)) and
// 12 ProductFiles on hand, we can calculate PercentCoverage as 50.00
type CoverageSummary struct {
	After            *time.Time `json:"after" db:"after"`
	Before           *time.Time `json:"before" db:"before"`
	ProductfileCount int        `json:"productfile_count" db:"productfile_count"`
	PercentCoverage  float32    `json:"percent_coverage" db:"coverage"`
}

// Productfile is a file associated with a product
type Productfile struct {
	ID       uuid.UUID `json:"id"`
	Datetime string    `json:"datetime"`
	File     string    `json:"file"`
}

// Availability stores
type Availability struct {
	ProductID  uuid.UUID   `json:"product_id"`
	DateCounts []DateCount `json:"date_counts"`
}

// DateCount is a date and a count
type DateCount struct {
	Date  time.Time `json:"date" db:"date"`
	Count int       `json:"count" db:"count"`
}

// ListProducts returns a list of products
func ListProducts(db *sqlx.DB) ([]Product, error) {
	sql := listProductsSQL()
	pp := make([]Product, 0)
	if err := db.Select(&pp, sql); err != nil {
		return make([]Product, 0), err
	}
	return pp, nil
}

// GetProduct returns a single product
func GetProduct(db *sqlx.DB, ID *uuid.UUID) (*Product, error) {
	sql := listProductsSQL() + " WHERE a.id = $1"
	var p Product
	if err := db.Get(&p, sql, ID); err != nil {
		return nil, err
	}
	return &p, nil
}

// GetProductProductfiles returns array of productfiles
func GetProductProductfiles(db *sqlx.DB, ID uuid.UUID, after string, before string) []Productfile {
	sql := `SELECT id, datetime, file FROM productfile
	         WHERE product_id = $1 AND
	               datetime >= $2 AND
	               datetime <= $3
	`
	rows, err := db.Query(sql, ID, after, before)

	if err != nil {
		panic(err)
	}

	defer rows.Close()
	result := make([]Productfile, 0)
	for rows.Next() {
		pf := Productfile{}
		var file string
		err := rows.Scan(&pf.ID, &pf.Datetime, &file)

		if err != nil {
			panic(err)
		}

		//pf.File = strings.Join([]string{"https://cumulus.rsgis.dev/apimedia", file}, "/")
		pf.File = strings.Join([]string{"https://api.rsgis.dev", file}, "/")

		result = append(result, pf)
	}
	return result
}

// GetProductAvailability returns Availability for a product
func GetProductAvailability(db *sqlx.DB, ID *uuid.UUID) (*Availability, error) {

	// https://stackoverflow.com/questions/29023336/generate-series-in-postgres-from-start-and-end-date-in-a-table
	sql := `SELECT series.day                      AS date,
	               COALESCE(daily_counts.count, 0) AS count
            FROM (
				SELECT generate_series(MIN(pf.datetime)::date, MAX(pf.datetime)::date, '1 Day') AS day
                FROM productfile pf
             	WHERE product_id = $1
			) series
			LEFT OUTER JOIN (
				SELECT datetime::date as day,
				COUNT(*) as count
				FROM productfile
				WHERE product_id = $1
				GROUP BY day
			) daily_counts ON daily_counts.day = series.day
	`
	a := Availability{ProductID: *ID, DateCounts: make([]DateCount, 0)}
	if err := db.Select(&a.DateCounts, sql, ID); err != nil {
		return nil, err
	}
	return &a, nil
}

func listProductsSQL() string {
	return `SELECT a.id                  AS id,
				   a.slug				 AS slug,
				   a.name                AS name,
				   a.group_id            AS group_id,
				   g.name                AS group,
				   a.is_realtime         AS is_realtime,
				   a.is_forecast         AS is_forecast,
	               a.temporal_resolution AS temporal_resolution,
	               a.temporal_duration   AS temporal_duration,
	               a.dss_fpart           AS dss_fpart,
				   a.description		 AS description,
	               p.name                AS parameter,
	               u.name                AS unit,
	               pf.after              AS after,
				   pf.before             AS before,
				   COALESCE(pf.productfile_count, 0)  AS productfile_count,
				   CASE WHEN pf.productfile_count IS NULL THEN 0
						WHEN pf.productfile_count = 0 THEN 0
				   		WHEN pf.productfile_count = 1 THEN 100
						WHEN pf.before = pf.after THEN 0
				        ELSE ROUND(
							(100*pf.productfile_count*a.temporal_resolution/EXTRACT('EPOCH' FROM age(pf.before, pf.after)))::numeric, 2
						) END AS coverage
            FROM product a
            JOIN unit u ON u.id = a.unit_id
			JOIN parameter p ON p.id = a.parameter_id
			LEFT JOIN product_group g ON a.group_id = g.id
            LEFT JOIN (
                SELECT product_id    AS product_id,
                       COUNT(id)     AS productfile_count,
                       MIN(datetime) AS after,
                       MAX(datetime) AS before
            	FROM productfile
                GROUP BY product_id
            ) AS pf ON pf.product_id = a.id
	`
}
