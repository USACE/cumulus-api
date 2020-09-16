package models

import (
	"log"
	"time"

	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
)

// KeyInfo is a record of a key issued for the system
// ID is unique identifier in database (not known to user)
// KeyID is a unique identifier that is known to the user
// and does not need to be treated like a secret
type KeyInfo struct {
	ID      uuid.UUID `json:"-"`
	KeyID   string    `json:"key_id" db:"key_id"`
	Issued  time.Time `json:"issued"`
	Hash    string    `json:"-"`
	Revoked bool      `json:"revoked"`
}

// CreateKeyInfo creates a key and returns the created key
// The actual plaintext key is only returned once when the
// key is created. Everything else works off a stored hash
func CreateKeyInfo(db *sqlx.DB, keyID *string, hash *string) (KeyInfo, error) {

	var ki KeyInfo
	if err := db.QueryRowx(
		`INSERT INTO key (key_id, hash, revoked) VALUES
		($1, $2, false)
		RETURNING key_id, issued, revoked
		`, keyID, hash,
	).StructScan(&ki); err != nil {
		return KeyInfo{}, err
	}

	return ki, nil
}

// ListKeyInfo returns an array of all key hashes
func ListKeyInfo(db *sqlx.DB) ([]KeyInfo, error) {
	var hh = make([]KeyInfo, 0)
	if err := db.Select(&hh, `SELECT * FROM key`); err != nil {
		return hh, err
	}
	return hh, nil
}

// MustListKeyInfo returns an array of all key hashes, panics on error
func MustListKeyInfo(db *sqlx.DB) []KeyInfo {
	kk, err := ListKeyInfo(db)
	if err != nil {
		log.Panicln("ERROR RETRIEVING VALID KEYS FROM DATABASE", err.Error())
	}
	return kk
}
