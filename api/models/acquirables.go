package models

import (
	"context"
	"time"

	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v4/pgxpool"
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
func ListAcquirables(db *pgxpool.Pool) ([]Acquirable, error) {
	nn := make([]Acquirable, 0)
	if err := pgxscan.Select(context.Background(), db, &nn, `SELECT id, name, slug FROM ACQUIRABLE`); err != nil {
		return make([]Acquirable, 0), err
	}
	return nn, nil
}

// GetAcquisitionAcquirablefiles returns array of productfiles
func ListAcquirablefiles(db *pgxpool.Pool, ID uuid.UUID, after string, before string) ([]Acquirablefile, error) {
	ff := make([]Acquirablefile, 0)
	if err := pgxscan.Select(
		context.Background(), db, &ff,
		`SELECT id, datetime, file, create_date, process_date, acquirable_id
		 FROM v_acquirablefile
	     WHERE acquirable_id = $1 AND datetime >= $2 AND datetime <= $3`, ID, after, before,
	); err != nil {
		return make([]Acquirablefile, 0), err
	}
	return ff, nil
}

func CreateAcquirablefiles(db *pgxpool.Pool, a Acquirablefile) (*Acquirablefile, error) {
	var aNew Acquirablefile
	if err := pgxscan.Get(
		context.Background(), db, &aNew,
		`INSERT INTO acquirablefile (datetime, file, acquirable_id)
		 VALUES($1, $2, $3) 
		 RETURNING id, datetime, file, create_date, process_date, acquirable_id`,
		a.Datetime, a.File, a.AcquirableID,
	); err != nil {
		return nil, err
	}
	return &aNew, nil
}
