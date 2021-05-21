package models

import (
	"context"

	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v4/pgxpool"
)

// ListMyWatersheds lists watersheds for a profileID
func ListMyWatersheds(db *pgxpool.Pool, profileID *uuid.UUID) ([]Watershed, error) {
	ww := make([]Watershed, 0)
	if err := pgxscan.Select(
		context.Background(), db, &ww,
		WatershedSQL+` FROM v_watershed w
		               WHERE w.id IN (SELECT watershed_id FROM my_watersheds WHERE profile_id=$1)
					   ORDER BY w.name`, profileID,
	); err != nil {
		return make([]Watershed, 0), nil
	}
	return ww, nil
}

// MyWatershedsAdd links a watershed to a profileID
func MyWatershedsAdd(db *pgxpool.Pool, profileID *uuid.UUID, watershedID *uuid.UUID) error {
	if _, err := db.Exec(
		context.Background(),
		`INSERT INTO my_watersheds (profile_id, watershed_id) VALUES ($1, $2)
		 ON CONFLICT ON CONSTRAINT profile_unique_watershed DO NOTHING`, profileID, watershedID,
	); err != nil {
		return err
	}
	return nil
}

// MyWatershedsRemove unlinks a watershed to a profileID
func MyWatershedsRemove(db *pgxpool.Pool, profileID *uuid.UUID, watershedID *uuid.UUID) error {
	if _, err := db.Exec(
		context.Background(),
		`DELETE FROM my_watersheds WHERE profile_id = $1 AND watershed_id = $2`, profileID, watershedID,
	); err != nil {
		return err
	}
	return nil
}
