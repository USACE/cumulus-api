package models

import (
	"context"
	"fmt"
	"time"

	// Postgres Database Driver
	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	_ "github.com/jackc/pgx/v4"
	"github.com/jackc/pgx/v4/pgxpool"
)

var listProductsSQL = `SELECT id, slug, name, label, tags, temporal_resolution, temporal_duration,
                              parameter_id, parameter, unit_id, unit, dss_fpart, description,
							  suite_id, suite, after, before, productfile_count, last_forecast_version
	                   FROM v_product`

// ProductInfo holds information required to create a product
type ProductInfo struct {
	Name               string    `json:"name"`
	TemporalResolution int       `json:"temporal_resolution" db:"temporal_resolution"`
	TemporalDuration   int       `json:"temporal_duration" db:"temporal_duration"`
	DssFpart           string    `json:"dss_fpart" db:"dss_fpart"`
	ParameterID        uuid.UUID `json:"parameter_id" db:"parameter_id"`
	Parameter          string    `json:"parameter"`
	UnitID             uuid.UUID `json:"unit_id" db:"unit_id"`
	Unit               string    `json:"unit"`
	Description        string    `json:"description"`
	SuiteID            uuid.UUID `json:"suite_id" db:"suite_id"`
	Suite              string    `json:"suite"`
	Label              string    `json:"label"`
}

type ProductIdentifiers struct {
	ID   uuid.UUID `json:"id"`
	Slug string    `json:"slug" db:"slug"`
}

// Product holds all information about a product
type Product struct {
	ProductIdentifiers
	Tags []uuid.UUID `json:"tags" db:"tags"`
	ProductInfo
	CoverageSummary
}

type ProductStatus struct {
	Slug                  string     `json:"slug" db:"slug"`
	LatestProductDatetime *time.Time `json:"latest_product_datetime" db:"latest_product_datetime"`
	AcceptableTimedelta   *string    `json:"acceptable_timedelta" db:"acceptable_timedelta"`
	ActualTimedelta       *string    `json:"actual_timedelta" db:"actual_timedelta"`
	IsCurrent             bool       `json:"is_current" db:"is_current"`
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
	After               *time.Time `json:"after" db:"after"`
	Before              *time.Time `json:"before" db:"before"`
	ProductfileCount    int        `json:"productfile_count" db:"productfile_count"`
	LastForecastVersion *time.Time `json:"last_forecast_version" db:"last_forecast_version"`
}

// Availability includes a date count for each product id
type Availability struct {
	ProductID  uuid.UUID   `json:"product_id"`
	DateCounts []DateCount `json:"date_counts"`
}

// DateCount is a date and a count
type DateCount struct {
	Date  time.Time `json:"date" db:"date"`
	Count int       `json:"count" db:"count"`
}

// GetProductIngestStatus
func GetProductIngestStatus(db *pgxpool.Pool) ([]ProductStatus, error) {
	ps := make([]ProductStatus, 0)
	productStatusSql := `SELECT slug, latest_product_datetime, acceptable_timedelta::text, 
						actual_timedelta::text, is_current FROM v_product_status`
	if err := pgxscan.Select(context.Background(), db, &ps, productStatusSql); err != nil {
		return make([]ProductStatus, 0), err
	}
	return ps, nil
}

// GetProductSlugs
func GetProductSlugs(db *pgxpool.Pool) (map[string]uuid.UUID, error) {
	pp := make([]ProductIdentifiers, 0)
	if err := pgxscan.Select(
		context.Background(), db, &pp, `SELECT id, slug FROM v_product`,
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

// ListProducts returns a list of products
func ListProducts(db *pgxpool.Pool) ([]Product, error) {
	pp := make([]Product, 0)
	if err := pgxscan.Select(context.Background(), db, &pp, listProductsSQL); err != nil {
		return make([]Product, 0), err
	}
	return pp, nil
}

// GetProduct returns a single product
func GetProduct(db *pgxpool.Pool, productID *uuid.UUID) (*Product, error) {
	var p Product
	if err := pgxscan.Get(context.Background(), db, &p, listProductsSQL+" WHERE id = $1", productID); err != nil {
		return nil, err
	}
	return &p, nil
}

// CreateProduct creates a single product
func CreateProduct(db *pgxpool.Pool, p *ProductInfo) (*Product, error) {

	// Helper Function to Build Slug
	// Slug First Pass is: <Suite Name> <Label || ""> <ParameterName> <TemporalResolution>
	nameFirstPass := func() (string, error) {

		sql := fmt.Sprintf(
			`SELECT s.name || ' ' || '%s' || p.name || ' ' || '%d' AS str 
			 FROM parameter p
			 CROSS JOIN (SELECT name FROM suite where id = $2) s
			 WHERE p.id = $1`, p.Label, p.TemporalResolution,
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
	slug, err := NextUniqueSlug(db, "product", "slug", s, "", "")
	if err != nil {
		return nil, err
	}

	// Insert Into Database Using New Slug
	var pID uuid.UUID
	if err := pgxscan.Get(
		context.Background(), db, &pID,
		`INSERT INTO product (temporal_resolution, temporal_duration, dss_fpart, parameter_id, unit_id, description, suite_id, label, slug) VALUES
			($1, $2, $3, $4, $5, $6, $7, $8, $9)
		RETURNING id`, p.TemporalResolution, p.TemporalDuration, p.DssFpart, p.ParameterID, p.UnitID, p.Description, p.SuiteID, p.Label, slug,
	); err != nil {
		return nil, err
	}
	return GetProduct(db, &pID)
}

// UpdateProduct updates a single product
func UpdateProduct(db *pgxpool.Pool, p *Product) (*Product, error) {
	var pID uuid.UUID
	if err := pgxscan.Get(
		context.Background(), db, &pID,
		`UPDATE product SET temporal_resolution=$2, temporal_duration=$3, dss_fpart=$4,
		                    parameter_id=$5, unit_id=$6, description=$7, suite_id=$8, label=$9 
		 WHERE id = $1
		 RETURNING id`, p.ID, p.TemporalResolution, p.TemporalDuration, p.DssFpart, p.ParameterID, p.UnitID, p.Description, p.SuiteID, p.Label,
	); err != nil {
		return nil, err
	}
	return GetProduct(db, &pID)
}

// DeleteProduct deletes a signle product
func DeleteProduct(db *pgxpool.Pool, pID *uuid.UUID) error {
	if _, err := db.Exec(context.Background(), `UPDATE product SET deleted=true WHERE id=$1`, pID); err != nil {
		return err
	}
	return nil
}

// UndeleteProduct undeletes a single product
func UndeleteProduct(db *pgxpool.Pool, pID *uuid.UUID) (*Product, error) {
	if _, err := db.Exec(context.Background(), `UPDATE product SET deleted=false WHERE id=$1`, pID); err != nil {
		return nil, err
	}
	return GetProduct(db, pID)
}

// GetProductAvailability returns Availability for a product
func GetProductAvailability(db *pgxpool.Pool, ID *uuid.UUID) (*Availability, error) {
	// https://stackoverflow.com/questions/29023336/generate-series-in-postgres-from-start-and-end-date-in-a-table
	a := Availability{ProductID: *ID, DateCounts: make([]DateCount, 0)}
	if err := pgxscan.Select(
		context.Background(), db, &a.DateCounts,
		`SELECT series.day                      AS date,
		        COALESCE(daily_counts.count, 0) AS count
		 FROM (
			 SELECT generate_series(MIN(pf.datetime)::date, MAX(pf.datetime)::date, '1 Day') AS day
			 FROM productfile pf
			 WHERE product_id = $1
		 ) series
		 LEFT OUTER JOIN (
			 SELECT datetime::date as day,
			        COUNT(*)       as count
			 FROM productfile
			 WHERE product_id = $1
			 GROUP BY day
		 ) daily_counts ON daily_counts.day = series.day`, ID,
	); err != nil {
		return nil, err
	}
	return &a, nil
}

func TagProduct(db *pgxpool.Pool, productID *uuid.UUID, tagID *uuid.UUID) (*Product, error) {
	if _, err := db.Exec(
		context.Background(),
		`INSERT INTO product_tags (product_id, tag_id) VALUES ($1, $2)
		 ON CONFLICT ON CONSTRAINT unique_tag_product DO NOTHING`,
		productID, tagID,
	); err != nil {
		return nil, err
	}
	return GetProduct(db, productID)
}

func UntagProduct(db *pgxpool.Pool, productID *uuid.UUID, tagID *uuid.UUID) (*Product, error) {
	if _, err := db.Exec(
		context.Background(), `DELETE FROM product_tags WHERE product_id=$1 AND tag_id=$2`, productID, tagID,
	); err != nil {
		return nil, err
	}
	return GetProduct(db, productID)
}
