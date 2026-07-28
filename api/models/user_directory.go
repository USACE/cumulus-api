package models

import (
	"context"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
)

// UserDirectory is a display-name cache keyed by sub, populated from JWT
// claims as users make requests. It is not a source of identity or auth.
type UserDirectory struct {
	Sub               uuid.UUID `json:"sub" db:"sub"`
	PreferredUsername *string   `json:"preferred_username" db:"preferred_username"`
	Email             *string   `json:"email" db:"email"`
	Name              *string   `json:"name" db:"name"`
	LastSeen          time.Time `json:"last_seen" db:"last_seen"`
}

// UserIdentity holds the display-name claims read off a request's JWT, for
// recording alongside a download. Any field may be nil if the claim was absent.
type UserIdentity struct {
	PreferredUsername *string
	Email             *string
	Name              *string
}

// IsEmpty reports whether there is nothing worth writing to user_directory --
// true for application-key and anonymous requests, which carry no claims.
func (u *UserIdentity) IsEmpty() bool {
	return u == nil || (u.PreferredUsername == nil && u.Email == nil && u.Name == nil)
}

// UpsertUserDirectory records/refreshes the display-name fields for a sub.
// Non-nil fields overwrite; nil fields leave the existing stored value alone.
//
// This runs inside the caller's transaction and is deliberately only called
// when a user requests a download package -- downloads are orders of magnitude
// rarer than authenticated requests, and the previous per-request version
// starved the pgxpool connection pool under sustained auth traffic (305db09).
func UpsertUserDirectory(ctx context.Context, tx pgx.Tx, sub uuid.UUID, ident *UserIdentity) error {
	if ident.IsEmpty() {
		return nil
	}
	_, err := tx.Exec(ctx,
		`INSERT INTO user_directory (sub, preferred_username, email, name, last_seen)
		 VALUES ($1, $2, $3, $4, now())
		 ON CONFLICT (sub) DO UPDATE SET
		     preferred_username = COALESCE(EXCLUDED.preferred_username, user_directory.preferred_username),
		     email              = COALESCE(EXCLUDED.email, user_directory.email),
		     name               = COALESCE(EXCLUDED.name, user_directory.name),
		     last_seen          = now()`,
		sub, ident.PreferredUsername, ident.Email, ident.Name,
	)
	return err
}
