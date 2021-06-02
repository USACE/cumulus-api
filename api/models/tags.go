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
type Tag struct {
	ID          uuid.UUID `json:"id"`
	Name        string    `json:"name"`
	Description string    `json:"description"`
	Color       string    `json:"color"`
}

func ListTags(db *pgxpool.Pool) ([]Tag, error) {
	tt := make([]Tag, 0)
	if err := pgxscan.Select(
		context.Background(), db, &tt,
		`SELECT id, name, description, color FROM tag`,
	); err != nil {
		return make([]Tag, 0), err
	}
	return tt, nil
}

func GetTag(db *pgxpool.Pool, tagID *uuid.UUID) (*Tag, error) {
	var t Tag
	if err := pgxscan.Get(
		context.Background(), db, &t,
		`SELECT id, name, description, color
		 FROM tag
		 WHERE id = $1`, &tagID,
	); err != nil {
		return nil, err
	}
	return &t, nil
}

func CreateTag(db *pgxpool.Pool, g *Tag) (*Tag, error) {
	var tNew Tag
	if err := pgxscan.Get(
		context.Background(), db, &tNew,
		`INSERT INTO tag (name, description, color) VALUES ($1, $2, $3)
		 RETURNING id, name, description, color`, g.Name, g.Description, g.Color,
	); err != nil {
		return nil, err
	}
	return &tNew, nil
}

func UpdateTag(db *pgxpool.Pool, g *Tag) (*Tag, error) {
	var tUpdated Tag
	if err := pgxscan.Get(
		context.Background(), db, &tUpdated,
		`UPDATE tag SET name=$2, description=$3, color=$4 WHERE id=$1
		 RETURNING id, name, description, color`, g.ID, g.Name, g.Description, g.Color,
	); err != nil {
		return nil, err
	}
	return &tUpdated, nil
}

func DeleteTag(db *pgxpool.Pool, id *uuid.UUID) error {
	if _, err := db.Exec(
		context.Background(),
		`DELETE FROM tag WHERE id=$1`, id,
	); err != nil {
		return err
	}
	return nil
}
