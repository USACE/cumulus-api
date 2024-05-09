package models

import (
	"context"

	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v4/pgxpool"
)

// Watershed is a watershed struct
type Watershed struct {
	ID           uuid.UUID   `json:"id"`
	OfficeSymbol *string     `json:"office_symbol" db:"office_symbol"`
	Slug         string      `json:"slug"`
	Name         string      `json:"name"`
	AreaGroups   []uuid.UUID `json:"area_groups" db:"area_groups"`
	Bbox         []float64   `json:"bbox" db:"bbox"`
}

// WatershedSQL includes common fields selected to build a watershed
const WatershedSQL = `SELECT w.id,
                             w.office_symbol,
                             w.slug,
                             w.name,
                             w.area_groups,
	                         ARRAY[
								 ST_XMin(w.geometry),
								 ST_Ymin(w.geometry),
								 ST_XMax(w.geometry),
								 ST_YMax(w.geometry)
							 ] AS bbox`

// ListWatersheds returns an array of watersheds
func ListWatersheds(db *pgxpool.Pool) ([]Watershed, error) {
	ww := make([]Watershed, 0)
	if err := pgxscan.Select(context.Background(), db, &ww, WatershedSQL+" FROM v_watershed w order by w.office_symbol, w.name"); err != nil {
		return make([]Watershed, 0), nil
	}
	return ww, nil
}

// GetWatershed returns a single watershed using slug
func GetWatershed(db *pgxpool.Pool, watershedID *uuid.UUID) (*Watershed, error) {
	var w Watershed
	if err := pgxscan.Get(
		context.Background(), db, &w, WatershedSQL+` FROM v_watershed w WHERE w.id = $1`, watershedID,
	); err != nil {
		return nil, err
	}
	return &w, nil
}

// GetDownloadWatershed returns the watershed for a downloadID
func GetDownloadWatershed(db *pgxpool.Pool, downloadID *uuid.UUID) (*Watershed, error) {
	var w Watershed
	if err := pgxscan.Get(
		context.Background(), db, &w, WatershedSQL+` FROM download d
		                                             INNER JOIN v_watershed w ON w.id = d.watershed_id
		                                             WHERE d.ID = $1`, downloadID,
	); err != nil {
		return nil, err
	}
	return &w, nil
}

// CreateWatershed creates a new watershed
func CreateWatershed(db *pgxpool.Pool, w *Watershed) (*Watershed, error) {
	slug, err := NextUniqueSlug(db, "watershed", "slug", w.Name, "", "")
	if err != nil {
		return nil, err
	}
	var wNew Watershed
	if err := pgxscan.Get(
		context.Background(), db, &wNew,
		`INSERT INTO watershed (name, slug) VALUES ($1,$2) RETURNING id, name, slug`, &w.Name, slug,
	); err != nil {
		return nil, err
	}
	return &wNew, nil
}

// UpdateWatershed updates a watershed
func UpdateWatershed(db *pgxpool.Pool, w *Watershed) (*Watershed, error) {
	var wID uuid.UUID
	if err := pgxscan.Get(context.Background(), db, &wID, `UPDATE watershed SET name=$1 WHERE id=$2 RETURNING id`, &w.Name, &w.ID); err != nil {
		return nil, err
	}
	return GetWatershed(db, &wID)
}

// DeleteWatershed deletes a watershed by slug
func DeleteWatershed(db *pgxpool.Pool, watershedID *uuid.UUID) error {
	if _, err := db.Exec(context.Background(), `UPDATE watershed SET deleted=true WHERE ID=$1`, watershedID); err != nil {
		return err
	}
	return nil
}

func UndeleteWatershed(db *pgxpool.Pool, watershedID *uuid.UUID) (*Watershed, error) {
	var wID uuid.UUID
	if err := pgxscan.Get(
		context.Background(), db, &wID, `UPDATE watershed SET deleted=false WHERE ID=$1 RETURNING id`, watershedID,
	); err != nil {
		return nil, err
	}
	return GetWatershed(db, &wID)
}
