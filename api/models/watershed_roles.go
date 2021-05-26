package models

import (
	"context"

	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v4/pgxpool"
)

// WatershedRole holds
type WatershedRole struct {
	ID        uuid.UUID `json:"id" db:"id"`
	ProfileID uuid.UUID `json:"profile_id" db:"profile_id"`
	Username  *string   `json:"username"`
	Email     string    `json:"email"`
	RoleID    uuid.UUID `json:"role_id" db:"role_id"`
	Role      string    `json:"role"`
}

// ListWatershedRoles lists users (profiles) who have permissions on a watershed and their role info
func ListWatershedRoles(db *pgxpool.Pool, watershedID *uuid.UUID) ([]WatershedRole, error) {
	rr := make([]WatershedRole, 0)
	if err := pgxscan.Select(
		context.Background(), db, &rr,
		`SELECT id, profile_id, username, email, role_id, role
		 FROM v_watershed_roles
		 WHERE watershed_id = $1
		 ORDER BY email`,
		watershedID,
	); err != nil {
		return make([]WatershedRole, 0), err
	}
	return rr, nil
}

// AddWatershedRole adds a role to a user for a specific watershed
func AddWatershedRole(db *pgxpool.Pool, watershedID, profileID, roleID, grantedBy *uuid.UUID) (*WatershedRole, error) {
	var id uuid.UUID
	// NOTE: DO UPDATE does not change underlying value;
	// UPDATE is needed so `RETURNING id` works under all conditions
	// https://stackoverflow.com/questions/34708509/how-to-use-returning-with-on-conflict-in-postgresql
	if err := pgxscan.Get(
		context.Background(), db, &id,
		`INSERT INTO watershed_roles (watershed_id, profile_id, role_id, granted_by)
	     VALUES ($1, $2, $3, $4)
		 ON CONFLICT ON CONSTRAINT unique_watershed_role DO UPDATE SET watershed_id = EXCLUDED.watershed_id
		 RETURNING id`, watershedID, profileID, roleID, grantedBy,
	); err != nil {
		return nil, err
	}

	var wr WatershedRole
	if err := pgxscan.Get(
		context.Background(), db, &wr,
		`SELECT id, profile_id, username, email, role_id, role
		 FROM v_watershed_roles
		 WHERE id = $1`,
		id,
	); err != nil {
		return nil, err
	}
	return &wr, nil
}

// RemoveWatershedRole removes a role from a user for a specific watershed
func RemoveWatershedRole(db *pgxpool.Pool, watershedID, profileID, roleID *uuid.UUID) error {
	if _, err := db.Exec(
		context.Background(),
		`DELETE FROM watershed_roles WHERE watershed_id = $1 AND profile_id = $2 AND role_id = $3`,
		watershedID, profileID, roleID,
	); err != nil {
		return err
	}
	return nil
}
