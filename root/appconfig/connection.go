package appconfig

import (
	"fmt"

	"github.com/jmoiron/sqlx"
)

// Connection returns a database connection
func Connection(cfg *Config) *sqlx.DB {
	connStr := func(cfg *Config) string {
		return fmt.Sprintf(
			"user=%s password=%s dbname=%s host=%s sslmode=%s binary_parameters=yes",
			cfg.DBUser, cfg.DBPass, cfg.DBName, cfg.DBHost, cfg.DBSSLMode,
		)
	}

	return sqlx.MustOpen("postgres", connStr(cfg))
}
