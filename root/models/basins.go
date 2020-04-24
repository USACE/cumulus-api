package models

import (
	"database/sql"
	"log"

	_ "github.com/lib/pq"
)

// Basin is a watershed struct
type Basin struct {
	ID     string `json:"id"`
	Name   string `json:"name"`
	Xmin   int    `json:"x_min"`
	Ymin   int    `json:"y_min"`
	Xmax   int    `json:"x_max"`
	Ymax   int    `json:"y_max"`
	Office string `json:"office_symbol"`
}

// ListBasins returns an array of basins
func ListBasins(db *sql.DB) []Basin {
	sql := `SELECT b.id,
				   b.name,
				   b.x_min,
				   b.y_min,
				   b.x_max,
				   b.y_max,
				   f.symbol
            FROM   offices_basin AS b
            JOIN offices_office  AS f
			  ON b.office_id = f.id
	`
	rows, err := db.Query(sql)

	if err != nil {
		panic(err)
	}

	defer rows.Close()
	result := make([]Basin, 0)
	for rows.Next() {
		b := Basin{}
		err := rows.Scan(
			&b.ID, &b.Name, &b.Xmin,
			&b.Ymin, &b.Xmax, &b.Ymax,
			&b.Office,
		)
		if err != nil {
			panic(err)
		}

		result = append(result, b)
	}
	return result
}

// GetBasin returns a single basin
func GetBasin(db *sql.DB, ID string) Basin {
	sql := `SELECT b.id,
				   b.name,
				   b.x_min,
				   b.y_min,
				   b.x_max,
				   b.y_max,
				   f.symbol
            FROM   offices_basin AS b
            JOIN offices_office  AS f
			  ON b.office_id = f.id
	        WHERE b.id = $1
	`
	var result Basin
	err := db.QueryRow(sql, ID).Scan(
		&result.ID, &result.Name, &result.Xmin,
		&result.Ymin, &result.Xmax, &result.Ymax,
		&result.Office,
	)

	if err != nil {
		log.Printf("Fail to query and scan row with ID %s;%s", ID, err)
	}

	return result
}
