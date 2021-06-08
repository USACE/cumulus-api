package models

import (

	// Postgres Database Driver

	"context"

	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	_ "github.com/jackc/pgx/v4"
	"github.com/jackc/pgx/v4/pgxpool"
)

// Parameter of a product
type Parameter struct {
	ID   uuid.UUID `json:"id"`
	Name string    `json:"name"`
}

func ListParameters(db *pgxpool.Pool) ([]Parameter, error) {
	pp := make([]Parameter, 0)
	if err := pgxscan.Select(
		context.Background(), db, &pp,
		`SELECT id, name FROM parameter order by name`,
	); err != nil {
		return make([]Parameter, 0), err
	}
	return pp, nil
}

func GetParameter(db *pgxpool.Pool, parameterID *uuid.UUID) (*Parameter, error) {
	var p Parameter
	if err := pgxscan.Get(
		context.Background(), db, &p,
		`SELECT id, name
		 FROM parameter
		 WHERE id = $1 order by name`, &parameterID,
	); err != nil {
		return nil, err
	}
	return &p, nil
}

func CreateParameter(db *pgxpool.Pool, g *Parameter) (*Parameter, error) {
	var pNew Parameter
	if err := pgxscan.Get(
		context.Background(), db, &pNew,
		`INSERT INTO parameter (name) VALUES ($1)
		 RETURNING id, name`, g.Name,
	); err != nil {
		return nil, err
	}
	return &pNew, nil
}

func UpdateParameter(db *pgxpool.Pool, g *Parameter) (*Parameter, error) {
	var pUpdated Parameter
	if err := pgxscan.Get(
		context.Background(), db, &pUpdated,
		`UPDATE parameter SET name=$2 WHERE id=$1
		 RETURNING id, name`, g.ID, g.Name,
	); err != nil {
		return nil, err
	}
	return &pUpdated, nil
}

func DeleteParameter(db *pgxpool.Pool, id *uuid.UUID) error {
	if _, err := db.Exec(
		context.Background(),
		`DELETE FROM parameter WHERE id=$1`, id,
	); err != nil {
		return err
	}
	return nil
}
