package models

import (
	"api/root/passwords"
	"time"

	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
)

// Profile is a user profile
type Profile struct {
	ID uuid.UUID `json:"id"`
	ProfileInfo
}

// ProfileInfo is information necessary to construct a profile
type ProfileInfo struct {
	EDIPI int    `json:"edipi"`
	Email string `json:"email"`
}

// TokenInfo represents the information held in the database about a token
// Note: Hash is stored, not the actual token
type TokenInfo struct {
	ID        uuid.UUID `json:"-"`
	TokenID   string    `json:"token_id" db:"token_id"`
	ProfileID uuid.UUID `json:"profile_id" db:"profile_id"`
	Issued    time.Time `json:"issued"`
	Hash      string    `json:"-"`
}

// Token includes all TokenInfo and the actual token string generated for a user
// this is only returned the first time a token is generated
type Token struct {
	SecretToken string `json:"secret_token"`
	TokenInfo
}

// GetProfileFromEDIPI returns a profile given an edipi
func GetProfileFromEDIPI(db *sqlx.DB, e int) (*Profile, error) {
	var p Profile
	if err := db.Get(
		&p, "SELECT * FROM profile WHERE edipi=$1", e,
	); err != nil {
		return nil, err
	}
	return &p, nil
}

// CreateProfile creates a new profile
func CreateProfile(db *sqlx.DB, n *ProfileInfo) (*Profile, error) {
	sql := "INSERT INTO profile (edipi, email) VALUES ($1, $2) RETURNING *"
	var p Profile
	if err := db.Get(&p, sql, n.EDIPI, n.Email); err != nil {
		return nil, err
	}
	return &p, nil
}

// CreateProfileToken creates a secret token and stores the HASH (not the actual token)
// to the database. The return payload of this function is the first and last time you'll see
// the raw token unless the user writes it down or stores it somewhere safe.
func CreateProfileToken(db *sqlx.DB, profileID *uuid.UUID) (*Token, error) {
	secretToken := passwords.GenerateRandom(40)
	tokenID := passwords.GenerateRandom(40)

	hash, err := passwords.CreateHash(secretToken, passwords.DefaultParams)
	if err != nil {
		return nil, err
	}
	var t Token
	if err := db.Get(
		&t, "INSERT INTO profile_token (token_id, profile_id, hash) VALUES ($1,$2,$3) RETURNING *",
		tokenID, profileID, hash,
	); err != nil {
		return nil, err
	}
	t.SecretToken = secretToken
	return &t, nil
}

// ListMyTokens returns TokenInfo for current logged-in user
func ListMyTokens(db *sqlx.DB, profileID *uuid.UUID) ([]TokenInfo, error) {
	tt := make([]TokenInfo, 0)
	if err := db.Select(
		&tt, "SELECT * FROM profile_token WHERE profile_id=$1", profileID,
	); err != nil {
		return make([]TokenInfo, 0), err
	}
	return tt, nil
}

// GetTokenInfoByTokenID returns a single token by token id
func GetTokenInfoByTokenID(db *sqlx.DB, tokenID *string) (*TokenInfo, error) {
	var n TokenInfo
	if err := db.Get(
		&n, "SELECT * FROM profile_token WHERE token_id=$1 LIMIT 1",
	); err != nil {
		return nil, err
	}
	return &n, nil
}