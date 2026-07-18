package models

import (
	"context"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
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

// UpsertUserDirectory records/refreshes the display-name fields for a sub.
// Non-nil fields overwrite; nil fields leave the existing stored value alone.
// The caller passes a context so the best-effort background refresh can be
// bounded with a timeout (avoids piling up connection-blocked goroutines if
// the DB is slow).
func UpsertUserDirectory(ctx context.Context, db *pgxpool.Pool, sub uuid.UUID, preferredUsername, email, name *string) error {
	_, err := db.Exec(ctx,
		`INSERT INTO user_directory (sub, preferred_username, email, name, last_seen)
		 VALUES ($1, $2, $3, $4, now())
		 ON CONFLICT (sub) DO UPDATE SET
		     preferred_username = COALESCE(EXCLUDED.preferred_username, user_directory.preferred_username),
		     email              = COALESCE(EXCLUDED.email, user_directory.email),
		     name               = COALESCE(EXCLUDED.name, user_directory.name),
		     last_seen          = now()`,
		sub, preferredUsername, email, name,
	)
	return err
}
