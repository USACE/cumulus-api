package models

import (
	"database/sql"
	"log"
	"strings"

	// Postgres Database Driver
	_ "github.com/lib/pq"
)

// Product is a product structure
type Product struct {
	ID                 string `json:"id"`
	Name               string `json:"name"`
	TemporalResolution string `json:"temporal_resolution"`
	TemporalDuration   string `json:"temporal_duration"`
	DssFpart           string `json:"dss_fpart"`
	Parameter          string `json:"parameter"`
	Unit               string `json:"unit"`
}

// Productfile is a file associated with a product
type Productfile struct {
	ID       string `json:"id"`
	Datetime string `json:"datetime"`
	File     string `json:"file"`
}

// ListProducts returns a list of products
func ListProducts(db *sql.DB) []Product {
	sql := `SELECT p.id,
	               p.name,
	               p.temporal_resolution,
	               p.temporal_duration,
				   p.dss_fpart,
				   products_parameter.name AS parameter,
	               products_unit.name AS unit
            FROM   products_product p
            JOIN products_unit
	          ON products_unit.id = p.unit_id
            JOIN products_parameter
	          ON products_parameter.id = p.parameter_id
	`

	rows, err := db.Query(sql)

	if err != nil {
		panic(err)
	}

	defer rows.Close()
	result := make([]Product, 0)
	for rows.Next() {
		p := Product{}
		err := rows.Scan(
			&p.ID,
			&p.Name,
			&p.TemporalResolution,
			&p.TemporalDuration,
			&p.DssFpart,
			&p.Parameter,
			&p.Unit,
		)
		if err != nil {
			panic(err)
		}

		result = append(result, p)
	}
	return result
}

// GetProduct returns a single basin
func GetProduct(db *sql.DB, ID string) Product {
	sql := `SELECT p.id,
                   p.name,
                   p.temporal_resolution,
                   p.temporal_duration,
                   p.dss_fpart,
                   products_parameter.name AS parameter,
                   products_unit.name AS unit
            FROM   products_product p
            JOIN products_unit
              ON products_unit.id = p.unit_id
            JOIN products_parameter
			  ON products_parameter.id = p.parameter_id
			WHERE p.id = $1
	`
	var result Product
	err := db.QueryRow(sql, ID).Scan(
		&result.ID,
		&result.Name,
		&result.TemporalResolution,
		&result.TemporalDuration,
		&result.DssFpart,
		&result.Parameter,
		&result.Unit,
	)

	if err != nil {
		log.Printf("Fail to query and scan row with ID %s;%s", ID, err)
	}

	return result
}

// GetProductProductfiles returns array of productfiles
func GetProductProductfiles(db *sql.DB, ID string, after string, before string) []Productfile {
	sql := `SELECT id, datetime, file FROM products_productfile
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
