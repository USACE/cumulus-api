package models

import (
	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
)

// Basin is a watershed struct
type Basin struct {
	ID     string `json:"id"`
	Name   string `json:"name"`
	Xmin   int    `json:"x_min" db:"x_min"`
	Ymin   int    `json:"y_min" db:"y_min"`
	Xmax   int    `json:"x_max" db:"x_max"`
	Ymax   int    `json:"y_max" db:"y_max"`
	Office string `json:"office_symbol" db:"office_symbol"`
}

// ListBasins returns an array of basins
func ListBasins(db *sqlx.DB) []Basin {
	sql := `SELECT b.id,
				   b.name,
				   b.x_min,
				   b.y_min,
				   b.x_max,
				   b.y_max,
				   f.symbol as office_symbol
            FROM   basin AS b
            JOIN   office  AS f
			  ON b.office_id = f.id
	`
	rows, err := db.Queryx(sql)

	if err != nil {
		panic(err)
	}

	defer rows.Close()
	result := make([]Basin, 0)
	for rows.Next() {
		var b Basin
		err = rows.StructScan(&b)
		if err != nil {
			panic(err)
		}
		result = append(result, b)
	}
	return result
}

// ListOfficeBasins lists basins for an office
func ListOfficeBasins(db *sqlx.DB, officeSlug string) ([]Basin, error) {
	sql := `SELECT b.id,
	               b.name,
	               b.x_min,
	               b.y_min,
	               b.x_max,
	               b.y_max,
	               f.symbol as office_symbol
			FROM   basin AS b
			JOIN   office  AS f ON b.office_id = f.id
			WHERE  f.symbol = $1
	`
	var bb []Basin
	err := db.Select(&bb, sql, officeSlug)
	if err != nil {
		return make([]Basin, 0), err
	}
	return bb, nil
}

// GetBasin returns a single basin
func GetBasin(db *sqlx.DB, ID *uuid.UUID) (*Basin, error) {
	sql := `SELECT b.id,
				   b.name,
				   b.x_min,
				   b.y_min,
				   b.x_max,
				   b.y_max,
				   f.symbol as office_symbol
            FROM   basin AS b
            JOIN office  AS f
			  ON b.office_id = f.id
	        WHERE b.id = $1
	`

	var b Basin
	if err := db.QueryRowx(sql, ID).StructScan(&b); err != nil {
		return nil, err
	}

	return &b, nil
}

// EnableBasinProductStatistics turns on statistics calculations when new productfiles arrive
// If attempting to "enable" when already "ENABLED", do nothing.
func EnableBasinProductStatistics(db *sqlx.DB, basinID *uuid.UUID, productID *uuid.UUID) error {
	if _, err := db.Exec(
		`INSERT INTO basin_product_statistics_enabled (basin_id, product_id) VALUES ($1, $2)
		 ON CONFLICT ON CONSTRAINT unique_basin_product DO NOTHING`,
		basinID, productID,
	); err != nil {
		return err
	}
	return nil
}

// DisableBasinProductStatistics turns off statistics calculatiions when new productfiles arrive
func DisableBasinProductStatistics(db *sqlx.DB, basinID *uuid.UUID, productID *uuid.UUID) error {
	if _, err := db.Exec(
		`DELETE FROM basin_product_statistics_enabled WHERE basin_id=$1 AND product_id=$2`,
		basinID, productID,
	); err != nil {
		return err
	}
	return nil
}
