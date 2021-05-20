package models

import (
	"context"
	"time"

	// Postgres Database Driver
	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	_ "github.com/jackc/pgx/v4"
	"github.com/jackc/pgx/v4/pgxpool"
)

var listProductsSQL = `SELECT id, slug, name, tags, temporal_resolution, temporal_duration,
                              parameter_id, parameter, unit_id, unit, dss_fpart, description
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
}

// Product holds all information about a product
type Product struct {
	ID   uuid.UUID   `json:"id"`
	Slug string      `json:"slug" db:"slug"`
	Tags []uuid.UUID `json:"tags" db:"tags"`
	ProductInfo
}

// Productfile is a file associated with a product
type Productfile struct {
	ID       uuid.UUID `json:"id"`
	Datetime time.Time `json:"datetime"`
	File     string    `json:"file"`
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
	// Assign Slug Based on Product Name; Slug Must Be Table Unique
	slug, err := NextUniqueSlug(db, "product", "slug", p.Name, "", "")
	if err != nil {
		return nil, err
	}
	var pID uuid.UUID
	if err := pgxscan.Get(
		context.Background(), db, &pID,
		`INSERT INTO product (slug, name, temporal_resolution, temporal_duration, dss_fpart, parameter_id, unit_id, description) VALUES
			($1, $2, $3, $4, $5, $6, $7, $8)
		RETURNING id`, slug, p.Name, p.TemporalResolution, p.TemporalDuration, p.DssFpart, p.ParameterID, p.UnitID, p.Description,
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
		`UPDATE product SET name=$2, temporal_resolution=$3, temporal_duration=$4, dss_fpart=$5,
		                    parameter_id=$6, unit_id=$7, description=$8
		 WHERE id = $1
		 RETURNING id`, p.ID, p.Name, p.TemporalResolution, p.TemporalDuration, p.DssFpart, p.ParameterID, p.UnitID, p.Description,
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

// ListProductfiles returns array of productfiles
func ListProductfiles(db *pgxpool.Pool, ID uuid.UUID, after string, before string) ([]Productfile, error) {
	ff := make([]Productfile, 0)
	if err := pgxscan.Select(
		context.Background(), db, &ff,
		`SELECT id, datetime, file
	     FROM productfile
		 WHERE product_id = $1 AND datetime >= $2 AND datetime <= $3`,
		ID, after, before,
	); err != nil {
		return make([]Productfile, 0), err
	}
	return ff, nil
}
