package models

import (
	"context"

	"github.com/georgysavva/scany/v2/pgxscan"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
)

type Office struct {
	ID     uuid.UUID `json:"id"`
	Symbol string    `json:"symbol"`
	Name   string    `json:"name"`
}

func ListOffices(db *pgxpool.Pool) ([]Office, error) {
	sql := `
SELECT
	o.id
	, o.symbol
	, o.name
FROM
	office o
	`
	var oo []Office
	err := pgxscan.Select(context.Background(), db, &oo, sql)
	return oo, err
}
