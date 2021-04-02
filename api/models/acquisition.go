package models

import (
	"strings"
	"time"

	"github.com/google/uuid"

	"github.com/jmoiron/sqlx"
)

//Acquirable is like a product, but not
type Acquirable struct {
	ID   uuid.UUID `json:"id"`
	Name string    `json:"name"`
	Slug string    `json:"slug"`
}

// Acquirablefile is a file associated with an acquirable
type Acquirablefile struct {
	ID           uuid.UUID  `json:"id"`
	Datetime     time.Time  `json:"datetime"`
	File         string     `json:"file"`
	CreateDate   time.Time  `json:"create_date" db:"create_date"`
	ProcessDate  *time.Time `json:"process_date" db:"process_date"`
	AcquirableID uuid.UUID  `json:"acquirable_id" db:"acquirable_id"`
}

// ListAcquirableInfo returns acquirable.Info from the database
func ListAcquirables(db *sqlx.DB) ([]Acquirable, error) {
	nn := make([]Acquirable, 0)
	if err := db.Select(&nn, `SELECT id, name, slug FROM ACQUIRABLE`); err != nil {
		return make([]Acquirable, 0), err
	}
	return nn, nil
}

// GetAcquisitionAcquirablefiles returns array of productfiles
func ListAcquirablefiles(db *sqlx.DB, ID uuid.UUID, after string, before string) ([]Acquirablefile, error) {
	sql := `SELECT id, datetime, file, create_date, process_date, acquirable_id FROM acquirablefile
	         WHERE acquirable_id = $1 AND
	               datetime >= $2 AND
	               datetime <= $3
	`
	rows, err := db.Query(sql, ID, after, before)

	if err != nil {
		return make([]Acquirablefile, 0), err
	}

	defer rows.Close()
	result := make([]Acquirablefile, 0)
	for rows.Next() {
		af := Acquirablefile{}
		var file string
		err := rows.Scan(&af.ID, &af.Datetime, &file, &af.CreateDate, &af.ProcessDate)

		if err != nil {
			return make([]Acquirablefile, 0), err
		}

		//pf.File = strings.Join([]string{"https://cumulus.rsgis.dev/apimedia", file}, "/")
		af.File = strings.Join([]string{"https://api.rsgis.dev", file}, "/")

		result = append(result, af)
	}
	return result, nil
}

func CreateAcquirablefiles(db *sqlx.DB, a Acquirablefile) (*Acquirablefile, error) {
	sql := `INSERT INTO acquirablefile (datetime, file, acquirable_id)
			VALUES($1, $2, $3) 
			RETURNING id, datetime, file, create_date, process_date, acquirable_id`

	var aNew Acquirablefile
	if err := db.Get(&aNew, sql, a.Datetime, a.File, a.AcquirableID); err != nil {
		return nil, err
	}

	return &aNew, nil
}
