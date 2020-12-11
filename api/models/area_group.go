package models

import (
	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
)

// AreaGroup is an area group
type AreaGroup struct {
	ID          uuid.UUID `json:"id" db:"id"`
	WatershedID uuid.UUID `json:"watershed_id" db:"watershed_id"`
	Slug        string `json:"slug" db:"slug"`
	Name        string `json:"name" db:"name"`
	Areas       []Area `json:"areas" db:"areas"`
}

// Area is an area; member of an AreaGroup
type Area struct {
	ID          uuid.UUID `json:"id" db:"id"`
	AreaGroupID uuid.UUID `json:"area_group_id" db:"area_group_id"`
	Slug        string `json:"slug" db:"slug"`
	Name        string `json:"name" db:"name"`
}

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
