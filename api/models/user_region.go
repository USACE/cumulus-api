package models

import (
	"context"
	"encoding/json"
	"time"

	"github.com/georgysavva/scany/v2/pgxscan"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

// UserRegion represents a user-defined geographic region
type UserRegion struct {
	ID          uuid.UUID       `json:"id" db:"id"`
	Sub         uuid.UUID       `json:"sub" db:"sub"`
	Name        string          `json:"name" db:"name"`
	Description *string         `json:"description,omitempty" db:"description"`
	GeoJSON     json.RawMessage `json:"geojson" db:"geojson"`
	Bbox        []float64       `json:"bbox" db:"bbox"`
	AreaSqKm    float64         `json:"area_sqkm" db:"area_sqkm"`
	CreatedAt   time.Time       `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time       `json:"updated_at" db:"updated_at"`
	IsPublic    bool            `json:"is_public" db:"is_public"`
	Tags        []string        `json:"tags,omitempty" db:"tags"`
	UsageCount  int             `json:"usage_count" db:"usage_count"`
}

// UserRegionInput represents the input for creating/updating a user region
type UserRegionInput struct {
	Name        string          `json:"name" validate:"required,min=1,max=255"`
	Description *string         `json:"description,omitempty"`
	GeoJSON     json.RawMessage `json:"geojson" validate:"required"`
	IsPublic    bool            `json:"is_public"`
	Tags        []string        `json:"tags,omitempty"`
}

// ListUserRegions returns all regions for a given user
func ListUserRegions(db *pgxpool.Pool, sub *uuid.UUID) ([]UserRegion, error) {
	regions := make([]UserRegion, 0)
	sql := `
		SELECT id, sub, name, description, geojson, bbox, area_sqkm, 
		       created_at, updated_at, is_public, tags, usage_count
		FROM v_user_region
		WHERE sub = $1
		ORDER BY updated_at DESC
	`
	if err := pgxscan.Select(context.Background(), db, &regions, sql, sub); err != nil {
		return nil, err
	}
	return regions, nil
}

// ListPublicUserRegions returns all public regions
func ListPublicUserRegions(db *pgxpool.Pool) ([]UserRegion, error) {
	regions := make([]UserRegion, 0)
	sql := `
		SELECT id, sub, name, description, geojson, bbox, area_sqkm, 
		       created_at, updated_at, is_public, tags, usage_count
		FROM v_user_region
		WHERE is_public = true
		ORDER BY usage_count DESC, updated_at DESC
		LIMIT 100
	`
	if err := pgxscan.Select(context.Background(), db, &regions, sql); err != nil {
		return nil, err
	}
	return regions, nil
}

// GetUserRegion returns a single user region by ID
func GetUserRegion(db *pgxpool.Pool, id *uuid.UUID, sub *uuid.UUID) (*UserRegion, error) {
	var region UserRegion
	sql := `
		SELECT id, sub, name, description, geojson, bbox, area_sqkm, 
		       created_at, updated_at, is_public, tags, usage_count
		FROM v_user_region
		WHERE id = $1 AND (sub = $2 OR is_public = true)
	`
	if err := pgxscan.Get(context.Background(), db, &region, sql, id, sub); err != nil {
		return nil, err
	}
	return &region, nil
}

// CreateUserRegion creates a new user region
func CreateUserRegion(db *pgxpool.Pool, sub *uuid.UUID, input *UserRegionInput) (*UserRegion, error) {
	var regionID uuid.UUID

	sql := `
		INSERT INTO user_region (sub, name, description, geojson, is_public, tags)
		VALUES ($1, $2, $3, $4, $5, $6)
		RETURNING id
	`

	err := db.QueryRow(
		context.Background(),
		sql,
		sub,
		input.Name,
		input.Description,
		string(input.GeoJSON),
		input.IsPublic,
		input.Tags,
	).Scan(&regionID)

	if err != nil {
		return nil, err
	}

	return GetUserRegion(db, &regionID, sub)
}

// UpdateUserRegion updates an existing user region
func UpdateUserRegion(db *pgxpool.Pool, id *uuid.UUID, sub *uuid.UUID, input *UserRegionInput) (*UserRegion, error) {
	sql := `
		UPDATE user_region
		SET name = $3, 
		    description = $4, 
		    geojson = $5, 
		    is_public = $6, 
		    tags = $7,
		    updated_at = NOW()
		WHERE id = $1 AND sub = $2
	`

	_, err := db.Exec(
		context.Background(),
		sql,
		id,
		sub,
		input.Name,
		input.Description,
		string(input.GeoJSON),
		input.IsPublic,
		input.Tags,
	)

	if err != nil {
		return nil, err
	}

	return GetUserRegion(db, id, sub)
}

// DeleteUserRegion deletes a user region
func DeleteUserRegion(db *pgxpool.Pool, id *uuid.UUID, sub *uuid.UUID) error {
	sql := `DELETE FROM user_region WHERE id = $1 AND sub = $2`

	result, err := db.Exec(context.Background(), sql, id, sub)
	if err != nil {
		return err
	}

	if result.RowsAffected() == 0 {
		return pgx.ErrNoRows
	}

	return nil
}

// SearchUserRegions searches for regions by name or tags
func SearchUserRegions(db *pgxpool.Pool, sub *uuid.UUID, query string) ([]UserRegion, error) {
	regions := make([]UserRegion, 0)
	sql := `
		SELECT id, sub, name, description, geojson, bbox, area_sqkm, 
		       created_at, updated_at, is_public, tags, usage_count
		FROM v_user_region
		WHERE (sub = $1 OR is_public = true)
		  AND (
		    name ILIKE '%' || $2 || '%' 
		    OR description ILIKE '%' || $2 || '%'
		    OR $2 = ANY(tags)
		  )
		ORDER BY 
		  CASE WHEN sub = $1 THEN 0 ELSE 1 END,
		  usage_count DESC,
		  updated_at DESC
		LIMIT 50
	`
	if err := pgxscan.Select(context.Background(), db, &regions, sql, sub, query); err != nil {
		return nil, err
	}
	return regions, nil
}
