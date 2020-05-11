package models

import (
	"time"

	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
)

// Token is
type Token struct {
	ID    string `json:"token_id"`
	Token string
}

// TokenHash is a record of a token issued for the system
type TokenHash struct {
	ID      uuid.UUID
	Issued  time.Time
	Hash    string
	Revoked bool
}

// CreateTokenHash creates a token and returns the created token
// The actual plaintext token is only returned once when the
// token is created. Everything else works off a stored hash
func CreateTokenHash(db *sqlx.DB, hash *string) error {

	txn := db.MustBegin()
	sql := `INSERT INTO token (hash, revoked) VALUES
			($1, false)
	`
	// Save Token ***HASH*** in database (not actual token)
	if _, err := txn.Exec(sql, *hash); err != nil {
		txn.Rollback()
		return err
	}

	txn.Commit()
	return nil
}

// ListTokenHashes returns an array of all token hashes in the database
func ListTokenHashes(db *sqlx.DB) ([]TokenHash, error) {
	var hh = make([]TokenHash, 0)
	if err := db.Select(&hh, `SELECT * FROM token`); err != nil {
		return hh, err
	}
	return hh, nil
}
