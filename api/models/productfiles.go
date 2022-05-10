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

// ListProductfiles returns array of productfiles
func ListProductfiles(db *pgxpool.Pool, ID uuid.UUID, after string, before string) ([]Productfile, error) {
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
