package models

import (
	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
)

// EnableAreaGroupProductStatistics turns on statistics for an area_group; If already "ENABLED", do nothing.
func EnableAreaGroupProductStatistics(db *sqlx.DB, agID *uuid.UUID, productID *uuid.UUID) error {
	if _, err := db.Exec(
		`INSERT INTO area_group_product_statistics_enabled (area_group_id, product_id) VALUES ($1, $2)
		 ON CONFLICT ON CONSTRAINT unique_area_group_product DO NOTHING`,
		agID, productID,
	); err != nil {
		return err
	}
	return nil
}

// DisableAreaGroupProductStatistics turns off statistics calculatiions for an area_group
func DisableAreaGroupProductStatistics(db *sqlx.DB, agID *uuid.UUID, productID *uuid.UUID) error {
	if _, err := db.Exec(
		`DELETE FROM area_group_product_statistics_enabled WHERE area_group_id=$1 AND product_id=$2`,
		agID, productID,
	); err != nil {
		return err
	}
	return nil
}
