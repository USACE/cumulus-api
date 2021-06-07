package models

import (

	// Postgres Database Driver

	"context"

	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	_ "github.com/jackc/pgx/v4"
	"github.com/jackc/pgx/v4/pgxpool"
)

// Tag is a tag that can be applied to a product
type Unit struct {
	ID           uuid.UUID `json:"id"`
	Name         string    `json:"name"`
	Abbreviation string    `json:"abbreviation"`
}

func ListUnits(db *pgxpool.Pool) ([]Unit, error) {
	uu := make([]Unit, 0)
	if err := pgxscan.Select(
		context.Background(), db, &uu,
		`SELECT id, name, abbreviation FROM unit`,
	); err != nil {
		return make([]Unit, 0), err
	}
	return uu, nil
}

func GetUnit(db *pgxpool.Pool, unitID *uuid.UUID) (*Unit, error) {
	var u Unit
	if err := pgxscan.Get(
		context.Background(), db, &u,
		`SELECT id, name, abbreviation
		 FROM unit
		 WHERE id = $1`, &unitID,
	); err != nil {
		return nil, err
	}
	return &u, nil
}

func CreateUnit(db *pgxpool.Pool, g *Unit) (*Unit, error) {
	var uNew Unit
	if err := pgxscan.Get(
		context.Background(), db, &uNew,
		`INSERT INTO unit (name, abbreviation) VALUES ($1, $2)
		 RETURNING id, name, abbreviation`, g.Name, g.Abbreviation,
	); err != nil {
		return nil, err
	}
	return &uNew, nil
}

func UpdateUnit(db *pgxpool.Pool, g *Unit) (*Unit, error) {
	var uUpdated Unit
	if err := pgxscan.Get(
		context.Background(), db, &uUpdated,
		`UPDATE unit SET name=$2, abbreviation=$3 WHERE id=$1
		 RETURNING id, name, abbreviation`, g.ID, g.Name, g.Abbreviation,
	); err != nil {
		return nil, err
	}
	return &uUpdated, nil
}

func DeleteUnit(db *pgxpool.Pool, id *uuid.UUID) error {
	if _, err := db.Exec(
		context.Background(),
		`DELETE FROM unit WHERE id=$1`, id,
	); err != nil {
		return err
	}
	return nil
}
