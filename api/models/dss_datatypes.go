package models

import (

	// Postgres Database Driver

	"context"

	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	_ "github.com/jackc/pgx/v4"
	"github.com/jackc/pgx/v4/pgxpool"
)

// DssDatatype of a product
type DssDatatype struct {
	ID   uuid.UUID `json:"id"`
	Name string    `json:"name"`
}

func ListDssDatatypes(db *pgxpool.Pool) ([]DssDatatype, error) {
	dd := make([]DssDatatype, 0)
	if err := pgxscan.Select(
		context.Background(), db, &dd,
		`SELECT id, name FROM dss_datatype order by name`,
	); err != nil {
		return make([]DssDatatype, 0), err
	}
	return dd, nil
}
