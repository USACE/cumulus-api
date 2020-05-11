package models

import (
	"encoding/json"

	"api/root/asyncfn"

	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
)

// Acquisition is a data retrieval request to AWS Lambda
type Acquisition struct {
	ID        uuid.UUID `json:"id"`
	Datetime  string    `json:"datetime"`
	ProductID uuid.UUID `json:"product_id" db:"product_id"`
}

// CreateAcquisition creates a Acquisition record and triggers AWS Lambda download
func CreateAcquisition(db *sqlx.DB, p Product) (Acquisition, error) {

	txn := db.MustBegin()
	sql := `INSERT INTO acquisition (product_id) VALUES
			($1)
			RETURNING id, datetime, product_id
	`

	// Create record of acquisition in database
	var a Acquisition
	if err := txn.QueryRowx(sql, p.ID).StructScan(&a); err != nil {
		txn.Rollback()
		return a, err
	}

	// AWS Lambda Event for Acquisition
	payload, err := json.Marshal(a)
	if err != nil {
		txn.Rollback()
		return Acquisition{}, err
	}

	// Invoke AWS Lambda
	if err := asyncfn.CallAsync(
		"corpsmap-cumulus-downloader",
		payload,
	); err != nil {
		txn.Rollback()
		return Acquisition{}, err
	}

	txn.Commit()
	return a, nil
}
