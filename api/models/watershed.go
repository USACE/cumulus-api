package models

import (
	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
)

// Watershed is a watershed struct
type Watershed struct {
	ID   uuid.UUID `json:"id"`
	Slug string    `json:"slug"`
	Name string    `json:"name"`
}

// ListWatersheds returns an array of watersheds
func ListWatersheds(db *sqlx.DB) ([]Watershed, error) {
	ww := make([]Watershed, 0)
	if err := db.Select(&ww, `SELECT id, slug, name FROM watershed`); err != nil {
		return make([]Watershed, 0), err
	}
	return ww, nil
}

// GetWatershed returns a single watershed using slug
func GetWatershed(db *sqlx.DB, id *uuid.UUID) (*Watershed, error) {
	var w Watershed
	if err := db.Get(&w, `SELECT id, slug, name FROM watershed WHERE id = $1`, id); err != nil {
		return nil, err
	}
	return &w, nil
}

// CreateWatershed creates a new watershed
func CreateWatershed(db *sqlx.DB, w *Watershed) (*Watershed, error) {
	slug, err := NextUniqueSlug(db, "watershed", "slug", w.Name, "", "")
	if err != nil {
		return nil, err
	}
	var wNew Watershed
	if err := db.Get(
		&wNew,
		`INSERT INTO watershed (name, slug) VALUES ($1,$2) 
		RETURNING id, name, slug`,
		&w.Name, slug,
	); err != nil {
		return nil, err
	}
	return &wNew, nil
}

// UpdateWatershed updates a watershed
func UpdateWatershed(db *sqlx.DB, w *Watershed) (*Watershed, error) {
	var wUpdated Watershed
	if err := db.Get(
		&wUpdated,
		`UPDATE watershed SET name=$1 WHERE id=$2
		 RETURNING id, slug, name`,
		&w.Name, &w.ID,
	); err != nil {
		return nil, err
	}
	return &wUpdated, nil
}

// DeleteWatershed deletes a watershed by slug
func DeleteWatershed(db *sqlx.DB, id *uuid.UUID) error {
	if _, err := db.Exec(
		`DELETE FROM watershed WHERE ID=$1`, id,
	); err != nil {
		return err
	}
	return nil
}
