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
	ID                 uuid.UUID `json:"id"`
	Name               string    `json:"name"`
	TemporalResolution string    `json:"temporal_resolution" db:"temporal_resolution"`
	TemporalDuration   string    `json:"temporal_duration" db:"temporal_duration"`
	DssFpart           string    `json:"dss_fpart" db:"dss_fpart"`
	Parameter          string    `json:"parameter"`
	Unit               string    `json:"unit"`
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
	After            time.Time `json:"after" db:"after"`
	Before           time.Time `json:"before" db:"before"`
	ProductfileCount int       `json:"productfile_count" db:"productfile_count"`
	PercentCoverage  float32   `json:"percent_coverage" db:"coverage"`
}

// Productfile is a file associated with a product
type Productfile struct {
	ID       uuid.UUID `json:"id"`
	Datetime string    `json:"datetime"`
	File     string    `json:"file"`
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

		pf.File = strings.Join([]string{"https://cumulus.rsgis.dev/apimedia", file}, "/")

		result = append(result, pf)
	}
	return result
}

func listProductsSQL() string {
	return `SELECT a.id                  AS id,
	               a.name                AS name,
	               a.temporal_resolution AS temporal_resolution,
	               a.temporal_duration   AS temporal_duration,
	               a.dss_fpart           AS dss_fpart,
	               p.name                AS parameter,
	               u.name                AS unit,
	               pf.after              AS after,
				   pf.before             AS before,
				   pf.productfile_count  AS productfile_count,
	               ROUND(
					   (100*pf.productfile_count*a.temporal_resolution/EXTRACT('EPOCH' FROM age(pf.before, pf.after)))::numeric, 2
	               ) AS coverage
            FROM product a
            JOIN unit u ON u.id = a.unit_id
            JOIN parameter p ON p.id = a.parameter_id
            JOIN (
                SELECT product_id    AS product_id,
                       COUNT(id)     AS productfile_count,
                       MIN(datetime) AS after,
                       MAX(datetime) AS before
            	FROM productfile
                GROUP BY product_id
            ) AS pf ON pf.product_id = a.id
	`
}
