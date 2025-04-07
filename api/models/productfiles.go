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

// Productfile is a file associated with a product
type Productfile struct {
	ProductID     uuid.UUID  `json:"product_id" db:"product_id"`
	ID            uuid.UUID  `json:"id"`
	Datetime      time.Time  `json:"datetime"`
	File          string     `json:"file"`
	Version       *time.Time `json:"version"`
	AcquirablesID *uuid.UUID `json:"acquirablefile_id" db:"acquirablefile_id"`
}

type ProductfileAvailability struct {
	Datetime    time.Time `json:"datetime"`
	IsAvailable bool      `json:"is_available"`
}

// ListProductFiles returns array of productfiles for a product
func ListProductFiles(db *pgxpool.Pool, ID uuid.UUID, after string, before string) ([]Productfile, error) {
	ff := make([]Productfile, 0)
	if err := pgxscan.Select(
		context.Background(), db, &ff,
		`SELECT product_id, id, datetime, file, version, acquirablefile_id
	     FROM productfile
		 WHERE product_id = $1 AND datetime >= $2 AND datetime <= $3`,
		ID, after, before,
	); err != nil {
		return make([]Productfile, 0), err
	}
	return ff, nil
}

// ListProductSeriesFiles returns array of productfiles for a product series
func ListProductSeriesFiles(db *pgxpool.Pool, ID uuid.UUID, after string, before string) ([]Productfile, error) {
	ff := make([]Productfile, 0)
	if err := pgxscan.Select(
		context.Background(), db, &ff,
		`SELECT product_id, id, datetime, file, version, acquirablefile_id
	     FROM productfile
		 WHERE product_id IN (
			SELECT id FROM product WHERE product_series_id = $1
		 ) AND datetime >= $2 AND datetime <= $3`,
		ID, after, before,
	); err != nil {
		return make([]Productfile, 0), err
	}
	return ff, nil
}

func GetProductFileAvailability(db *pgxpool.Pool, ID uuid.UUID, interval string, d time.Time) ([]ProductfileAvailability, error) {
	avail := make([]ProductfileAvailability, 0)
	startTime := time.Date(d.Year(), d.Month(), d.Day(), 0, 0, 0, 0, d.Location()).Format(time.RFC3339)
	endTime := time.Date(d.Year(), d.Month(), d.Day(), 23, 0, 0, 0, d.Location()).Format(time.RFC3339)
	if err := pgxscan.Select(context.Background(), db, &avail,
		`WITH hours AS (
				SELECT generate_series(
						$1::timestamp,  -- Start of the interval
						$2::timestamp,  -- End of the interval
						$3::interval
				) AS hour
		)
		SELECT 
				h.hour as datetime,
				CASE 
						WHEN pf.datetime IS NOT NULL THEN TRUE
						ELSE FALSE
				END AS is_available
		FROM 
				hours h
		LEFT JOIN (
			select * from productfile where product_id = $4 and datetime >= $5 and datetime <= $6
		) pf ON date_trunc('hour', pf.datetime) = h.hour
		ORDER BY 
				h.hour`, startTime, endTime, interval, ID, startTime, endTime,
	); err != nil {
		return make([]ProductfileAvailability, 0), err
	}
	return avail, nil
}

// CreateProductfiles creates productfiles from an array of productfiles
func CreateProductfiles(db *pgxpool.Pool, ff []Productfile) (int, error) {
	savedCount := 0
	tx, err := db.Begin(context.Background())
	if err != nil {
		return 0, err
	}
	defer tx.Rollback(context.Background())
	for _, f := range ff {
		if f.Version != nil {
			if _, err := tx.Exec(
				context.Background(),
				`INSERT INTO productfile (datetime, file, product_id, version, acquirablefile_id) VALUES ($1, $2, $3, $4, $5)
				 ON CONFLICT ON CONSTRAINT unique_product_version_datetime DO UPDATE SET update_date = CURRENT_TIMESTAMP`,
				f.Datetime, f.File, f.ProductID, f.Version, f.AcquirablesID,
			); err != nil {
				return 0, err
			}
		} else {
			if _, err := tx.Exec(
				context.Background(),
				`INSERT INTO productfile (datetime, file, product_id, acquirablefile_id) VALUES ($1, $2, $3, $4)
				 ON CONFLICT ON CONSTRAINT unique_product_version_datetime DO UPDATE SET update_date = CURRENT_TIMESTAMP`,
				f.Datetime, f.File, f.ProductID, f.AcquirablesID,
			); err != nil {
				return 0, err
			}
		}
		savedCount += 1
	}
	err = tx.Commit(context.Background())
	if err != nil {
		return 0, err
	}
	return savedCount, nil
}
