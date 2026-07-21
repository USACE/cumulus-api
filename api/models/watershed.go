package models

import (
	"context"
	"encoding/json"

	"github.com/georgysavva/scany/v2/pgxscan"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
)

// Watershed is a watershed struct
type Watershed struct {
	ID           uuid.UUID       `json:"id"`
	OfficeSymbol *string         `json:"office_symbol" db:"office_symbol"`
	OfficeID     *uuid.UUID      `json:"office_id" db:"office_id"`
	Slug         string          `json:"slug"`
	Name         string          `json:"name"`
	AreaGroups   []uuid.UUID     `json:"area_groups" db:"area_groups"`
	GeoJSON      json.RawMessage `json:"geojson" db:"geojson"`
	Bbox         []float64       `json:"bbox" db:"bbox"`
}

// WatershedInput is the payload for creating/updating a watershed
type WatershedInput struct {
	Name     string          `json:"name"`
	OfficeID *uuid.UUID      `json:"office_id"`
	GeoJSON  json.RawMessage `json:"geojson"`
}

// geojsonArg returns a *string suitable for passing raw GeoJSON to postgres,
// or nil when no geometry was provided (so existing geometry is left untouched).
func geojsonArg(raw json.RawMessage) *string {
	if len(raw) == 0 || string(raw) == "null" {
		return nil
	}
	s := string(raw)
	return &s
}

// WatershedSQL includes common fields selected to build a watershed.
// office_id and geojson are computed on request so the underlying view is
// left unchanged; geometry is reprojected to EPSG:4326 for web-map display.
const WatershedSQL = `SELECT w.id,
                             w.office_symbol,
                             (SELECT o.id FROM office o WHERE o.symbol = w.office_symbol) AS office_id,
                             w.slug,
                             w.name,
                             w.area_groups,
                             ST_AsGeoJSON(ST_Transform(w.geometry, 4326)) AS geojson,
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

// CreateWatershed creates a new watershed. GeoJSON (EPSG:4326) is optional and,
// when provided, is reprojected to the stored SRID (EPSG:5070).
func CreateWatershed(db *pgxpool.Pool, in *WatershedInput) (*Watershed, error) {
	slug, err := NextUniqueSlug(db, "watershed", "slug", in.Name, "", "")
	if err != nil {
		return nil, err
	}
	var wID uuid.UUID
	sql := `INSERT INTO watershed (name, slug, office_id, geometry)
	        VALUES ($1, $2, $3,
	            CASE WHEN $4::text IS NULL THEN NULL
	                 ELSE ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON($4), 4326), 5070) END)
	        RETURNING id`
	if err := db.QueryRow(
		context.Background(), sql, in.Name, slug, in.OfficeID, geojsonArg(in.GeoJSON),
	).Scan(&wID); err != nil {
		return nil, err
	}
	return GetWatershed(db, &wID)
}

// UpdateWatershed updates a watershed's name, office assignment and (optionally)
// its extent. A nil/empty geojson leaves the existing geometry untouched.
func UpdateWatershed(db *pgxpool.Pool, watershedID *uuid.UUID, in *WatershedInput) (*Watershed, error) {
	var wID uuid.UUID
	sql := `UPDATE watershed SET
	            name = $2,
	            office_id = $3,
	            geometry = CASE WHEN $4::text IS NULL THEN geometry
	                            ELSE ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON($4), 4326), 5070) END
	        WHERE id = $1
	        RETURNING id`
	if err := pgxscan.Get(
		context.Background(), db, &wID, sql, watershedID, in.Name, in.OfficeID, geojsonArg(in.GeoJSON),
	); err != nil {
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
