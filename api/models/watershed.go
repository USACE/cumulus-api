package models

import (
	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	"github.com/lib/pq"
)

// Watershed is a watershed struct
type Watershed struct {
	ID           uuid.UUID   `json:"id"`
	OfficeSymbol *string     `json:"office_symbol" db:"office_symbol"`
	Slug         string      `json:"slug"`
	Name         string      `json:"name"`
	AreaGroups   []uuid.UUID `json:"area_groups" db:"area_groups"`
	Bbox         []float64   `json:"bbox"`
}

// WatershedSQL includes common fields selected to build a watershed
const WatershedSQL = `SELECT w.id,
                             w.slug,
                             w.name,
                             w.area_groups,
						     ST_XMin(w.geometry) AS x_min,
						     ST_Ymin(w.geometry) AS y_min,
						     ST_XMax(w.geometry) AS x_max,
							 ST_YMax(w.geometry) AS y_max
							 `

// WatershedsFactory converts query rows to an array of watersheds
func WatershedsFactory(rows *sqlx.Rows) ([]Watershed, error) {
	defer rows.Close()
	ww := make([]Watershed, 0)
	for rows.Next() {
		var w Watershed
		w.Bbox = make([]float64, 4)
		if err := rows.Scan(
			&w.ID, &w.Slug, &w.Name, pq.Array(&w.AreaGroups),
			&w.Bbox[0], &w.Bbox[1], &w.Bbox[2], &w.Bbox[3],
		); err != nil {
			return make([]Watershed, 0), nil
		}
		ww = append(ww, w)
	}
	return ww, nil
}

// ListWatersheds returns an array of watersheds
func ListWatersheds(db *sqlx.DB) ([]Watershed, error) {
	rows, err := db.Queryx(WatershedSQL + " FROM v_watershed w")
	if err != nil {
		return make([]Watershed, 0), nil
	}
	return WatershedsFactory(rows)
}

// GetWatershed returns a single watershed using slug
func GetWatershed(db *sqlx.DB, id *uuid.UUID) (*Watershed, error) {
	rows, err := db.Queryx(WatershedSQL+` FROM v_watershed w WHERE w.id = $1`, id)
	if err != nil {
		return nil, err
	}
	ww, err := WatershedsFactory(rows)
	if err != nil {
		return nil, err
	}
	return &ww[0], nil
}

// GetDownloadWatershed returns the watershed for a downloadID
func GetDownloadWatershed(db *sqlx.DB, downloadID *uuid.UUID) (*Watershed, error) {

	rows, err := db.Queryx(
		WatershedSQL+` FROM download d
					   INNER JOIN v_watershed w ON w.id = d.watershed_id
					   WHERE d.ID = $1`, downloadID,
	)
	if err != nil {
		return nil, err
	}
	ww, err := WatershedsFactory(rows)
	if err != nil {
		return nil, err
	}
	return &ww[0], nil
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
