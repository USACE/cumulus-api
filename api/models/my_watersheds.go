package models

import (
	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
)

// ListMyWatersheds lists watersheds for a profileID
func ListMyWatersheds(db *sqlx.DB, profileID *uuid.UUID) ([]Watershed, error) {
	rows, err := db.Queryx(
		WatershedSQL+` FROM v_watershed w
		               WHERE w.id IN (
						   SELECT watershed_id FROM my_watersheds WHERE profile_id = $1
					   )
					   ORDER BY w.name`, profileID,
	)
	if err != nil {
		return make([]Watershed, 0), nil
	}
	return WatershedsFactory(rows)
}

// MyWatershedsAdd links a watershed to a profileID
func MyWatershedsAdd(db *sqlx.DB, profileID *uuid.UUID, watershedID *uuid.UUID) error {
	if _, err := db.Exec(
		`INSERT INTO my_watersheds (profile_id, watershed_id) VALUES ($1, $2)`,
		profileID, watershedID,
	); err != nil {
		return err
	}
	return nil
}

// MyWatershedsRemove unlinks a watershed to a profileID
func MyWatershedsRemove(db *sqlx.DB, profileID *uuid.UUID, watershedID *uuid.UUID) error {
	if _, err := db.Exec(
		`DELETE FROM my_watersheds WHERE profile_id = $1 AND watershed_id = $2`, profileID, watershedID,
	); err != nil {
		return err
	}
	return nil
}
