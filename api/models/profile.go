package models

import (
	"context"
	"time"

	"github.com/USACE/cumulus-api/api/passwords"

	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v4/pgxpool"
)

// Profile is a user profile
type Profile struct {
	ID uuid.UUID `json:"id"`
	ProfileInfo
	Tokens  []TokenInfoProfile `json:"tokens"`
	IsAdmin bool               `json:"is_admin" db:"is_admin"`
	Roles   []string           `json:"roles"`
}

func (p *Profile) attachTokens(db *pgxpool.Pool) error {
	if err := pgxscan.Select(
		context.Background(), db, &p.Tokens,
		`SELECT token_id, issued
		 FROM profile_token
		 WHERE profile_id=$1`, p.ID,
	); err != nil {
		return err
	}
	return nil
}

// TokenInfoProfile is token information embedded in Profile
type TokenInfoProfile struct {
	TokenID string    `json:"token_id" db:"token_id"`
	Issued  time.Time `json:"issued"`
}

// ProfileInfo is information necessary to construct a profile
type ProfileInfo struct {
	EDIPI    int    `json:"-"`
	Username string `json:"username"`
	Email    string `json:"email"`
}

// TokenInfo represents the information held in the database about a token
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
func GetProfileFromEDIPI(db *pgxpool.Pool, e int) (*Profile, error) {
	p := Profile{Tokens: make([]TokenInfoProfile, 0)}
	if err := pgxscan.Get(
		context.Background(), db, &p,
		"SELECT id, edipi, username, email, is_admin, roles FROM v_profile WHERE edipi=$1", e,
	); err != nil {
		return nil, err
	}
	if err := p.attachTokens(db); err != nil {
		return nil, err
	}
	return &p, nil
}

func GetProfileFromTokenID(db *pgxpool.Pool, tokenID string) (*Profile, error) {
	var p Profile
	if err := pgxscan.Get(
		context.Background(), db, &p,
		`SELECT p.id, p.edipi, p.username, p.email, p.is_admin, p.roles
		 FROM profile_token t
		 LEFT JOIN v_profile p ON p.id = t.profile_id
		 WHERE t.token_id=$1`, tokenID,
	); err != nil {
		return nil, err
	}
	if err := p.attachTokens(db); err != nil {
		return nil, err
	}
	return &p, nil
}

// CreateProfile creates a new profile
func CreateProfile(db *pgxpool.Pool, n *ProfileInfo) (*Profile, error) {
	p := Profile{
		Tokens: make([]TokenInfoProfile, 0),
		Roles:  make([]string, 0),
	}
	if err := pgxscan.Get(
		context.Background(), db, &p,
		`INSERT INTO profile (edipi, username, email) VALUES ($1, $2, $3)
		 RETURNING id, username, email`, n.EDIPI, n.Username, n.Email,
	); err != nil {
		return nil, err
	}
	return &p, nil
}

// CreateProfileToken creates a secret token and stores the HASH (not the actual token)
// to the database. The return payload of this function is the first and last time you'll see
// the raw token unless the user writes it down or stores it somewhere safe.
func CreateProfileToken(db *pgxpool.Pool, profileID *uuid.UUID) (*Token, error) {
	secretToken := passwords.GenerateRandom(40)
	tokenID := passwords.GenerateRandom(40)

	hash, err := passwords.CreateHash(secretToken, passwords.DefaultParams)
	if err != nil {
		return nil, err
	}
	var t Token
	if err := pgxscan.Get(
		context.Background(), db, &t,
		"INSERT INTO profile_token (token_id, profile_id, hash) VALUES ($1,$2,$3) RETURNING *",
		tokenID, profileID, hash,
	); err != nil {
		return nil, err
	}
	t.SecretToken = secretToken
	return &t, nil
}

// GetTokenInfoByTokenID returns a single token by token id
func GetTokenInfoByTokenID(db *pgxpool.Pool, tokenID *string) (*TokenInfo, error) {
	var n TokenInfo
	if err := pgxscan.Get(
		context.Background(), db, &n,
		`SELECT id, token_id, profile_id, issued, hash
		 FROM profile_token
		 WHERE token_id=$1
		 LIMIT 1`, tokenID,
	); err != nil {
		return nil, err
	}
	return &n, nil
}

// DeleteToken deletes a token by token_id
func DeleteToken(db *pgxpool.Pool, profileID *uuid.UUID, tokenID *string) error {
	if _, err := db.Exec(
		context.Background(), "DELETE FROM profile_token WHERE profile_id=$1 AND token_id=$2", profileID, tokenID,
	); err != nil {
		return err
	}
	return nil
}

// GrantApplicationAdmin adds application admin permission to an account
func GrantApplicationAdmin(db *pgxpool.Pool, profileID *uuid.UUID) error {
	if _, err := db.Exec(
		context.Background(), "UPDATE profile SET is_admin=true WHERE id=$1", profileID,
	); err != nil {
		return err
	}
	return nil
}

// RevokeApplicationAdmin removes application admin permission from an account
func RevokeApplicationAdmin(db *pgxpool.Pool, profileID *uuid.UUID) error {
	if _, err := db.Exec(
		context.Background(), "UPDATE profile SET is_admin=false WHERE id=$1", profileID,
	); err != nil {
		return err
	}
	return nil
}
