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
type Suite struct {
	ID          uuid.UUID `json:"id"`
	Name        string    `json:"name"`
	Slug        string    `json:"slug"`
	Description string    `json:"description"`
}

func ListSuites(db *pgxpool.Pool) ([]Suite, error) {
	ss := make([]Suite, 0)
	if err := pgxscan.Select(
		context.Background(), db, &ss,
		`SELECT id, name, slug, description FROM suite order by name`,
	); err != nil {
		return make([]Suite, 0), err
	}
	return ss, nil
}

func GetSuite(db *pgxpool.Pool, suiteID *uuid.UUID) (*Suite, error) {
	var s Suite
	if err := pgxscan.Get(
		context.Background(), db, &s,
		`SELECT id, name, slug, description
		 FROM suite
		 WHERE id = $1`, &suiteID,
	); err != nil {
		return nil, err
	}
	return &s, nil
}

func CreateSuite(db *pgxpool.Pool, s *Suite) (*Suite, error) {
	var sNew Suite
	if err := pgxscan.Get(
		context.Background(), db, &sNew,
		`INSERT INTO suite (name, slug, description) VALUES ($1, $2, $3)
		 RETURNING id, name, slug, description`, s.Name, s.Slug, s.Description,
	); err != nil {
		return nil, err
	}
	return &sNew, nil
}

func UpdateSuite(db *pgxpool.Pool, s *Suite) (*Suite, error) {
	var sUpdated Suite
	if err := pgxscan.Get(
		context.Background(), db, &sUpdated,
		`UPDATE suite SET name=$2, slug=$3, description=$4 WHERE id=$1
		 RETURNING id, name, slug, description`, s.ID, s.Name, s.Slug, s.Description,
	); err != nil {
		return nil, err
	}
	return &sUpdated, nil
}

func DeleteSuite(db *pgxpool.Pool, id *uuid.UUID) error {
	if _, err := db.Exec(
		context.Background(),
		`DELETE FROM suite WHERE id=$1`, id,
	); err != nil {
		return err
	}
	return nil
}
