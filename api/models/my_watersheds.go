package models

import (
	"context"

	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v4/pgxpool"
)

// ListMyWatersheds lists watersheds for a sub
func ListMyWatersheds(db *pgxpool.Pool, sub *uuid.UUID) ([]Watershed, error) {
	ww := make([]Watershed, 0)
	if err := pgxscan.Select(
		context.Background(), db, &ww,
		WatershedSQL+` FROM v_watershed w
		               WHERE w.id IN (SELECT watershed_id FROM my_watersheds WHERE sub=$1)
					   ORDER BY w.name`, sub,
	); err != nil {
		return make([]Watershed, 0), nil
	}
	return ww, nil
}

// MyWatershedsAdd links a watershed to a sub
func MyWatershedsAdd(db *pgxpool.Pool, sub *uuid.UUID, watershedID *uuid.UUID) error {
	if _, err := db.Exec(
		context.Background(),
		`INSERT INTO my_watersheds (sub, watershed_id) VALUES ($1, $2)
		 ON CONFLICT ON CONSTRAINT sub_unique_watershed DO NOTHING`, sub, watershedID,
	); err != nil {
		return err
	}
	return nil
}

// MyWatershedsRemove unlinks a watershed to a sub
func MyWatershedsRemove(db *pgxpool.Pool, sub *uuid.UUID, watershedID *uuid.UUID) error {
	if _, err := db.Exec(
		context.Background(),
		`DELETE FROM my_watersheds WHERE sub = $1 AND watershed_id = $2`, sub, watershedID,
	); err != nil {
		return err
	}
	return nil
}
