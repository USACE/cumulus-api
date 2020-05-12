package models

import (
	"strings"

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
}

// ProductAcquirable is a name and a schedule
type ProductAcquirable struct {
	ID       uuid.UUID `json:"id"`
	Name     string    `json:"name"`
	Schedule string    `json:"schedule"`
}

// Productfile is a file associated with a product
type Productfile struct {
	ID       uuid.UUID `json:"id"`
	Datetime string    `json:"datetime"`
	File     string    `json:"file"`
}

// ListProductsAcquirable is a raw product that can be downloaded
func ListProductsAcquirable(db *sqlx.DB) ([]ProductAcquirable, error) {
	pa := make([]ProductAcquirable, 0)
	if err := db.Select(&pa, `SELECT * FROM product_acquirable`); err != nil {
		return []ProductAcquirable{}, err
	}
	return pa, nil
}

// ListProducts returns a list of products
func ListProducts(db *sqlx.DB) []Product {
	sql := `SELECT p.id,
	               p.name,
	               p.temporal_resolution,
	               p.temporal_duration,
				   p.dss_fpart,
				   parameter.name AS parameter,
	               unit.name AS unit
            FROM   product p
            JOIN unit
	          ON unit.id = p.unit_id
            JOIN parameter
	          ON parameter.id = p.parameter_id
	`

	rows, err := db.Queryx(sql)

	if err != nil {
		panic(err)
	}

	defer rows.Close()
	result := make([]Product, 0)
	for rows.Next() {
		var p Product
		err = rows.StructScan(&p)
		if err != nil {
			panic(err)
		}
		result = append(result, p)
	}
	return result
}

// GetProduct returns a single product
func GetProduct(db *sqlx.DB, ID uuid.UUID) Product {
	sql := `SELECT p.id,
                   p.name,
                   p.temporal_resolution,
                   p.temporal_duration,
                   p.dss_fpart,
                   parameter.name AS parameter,
                   unit.name AS unit
            FROM   product p
            JOIN unit
              ON unit.id = p.unit_id
            JOIN parameter
			  ON parameter.id = p.parameter_id
			WHERE p.id = $1
	`
	var result Product
	if err := db.QueryRowx(sql, ID).StructScan(&result); err != nil {
		return result
	}

	return result
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
