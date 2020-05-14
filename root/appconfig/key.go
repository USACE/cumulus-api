package appconfig

import (
	"api/root/models"
	"api/root/passwords"

	"github.com/labstack/echo"
	"github.com/labstack/echo/middleware"
)

func keyAuthValidator(cfg *Config) middleware.KeyAuthValidator {
	return func(key string, c echo.Context) (bool, error) {

		db := Connection(cfg)

		// Get hash from database
		hashes, err := models.ListKeyInfo(db)
		if err != nil {
			return false, err
		}

		// Check if key matches a valid hash in the database
		for _, hash := range hashes {
			match, err := passwords.ComparePasswordAndHash(key, hash.Hash)
			if err != nil {
				return false, err
			}
			if match && !hash.Revoked {
				return true, nil
			}
		}

		return false, nil
	}
}

func keyAuthSkipper(cfg *Config) middleware.Skipper {
	return func(c echo.Context) bool {

		if cfg.KeyAuthDisabled {
			return true
		}
		// If JWT is not disabled and key is not in querystring
		if !cfg.JWTAuthDisabled && c.QueryParam("key") == "" {
			return true
		}
		return false
	}
}

// KeyAuthConfig supports Key-Based Authentication for the API
func KeyAuthConfig(cfg *Config) *middleware.KeyAuthConfig {
	return &middleware.KeyAuthConfig{
		Skipper:   keyAuthSkipper(cfg),
		Validator: keyAuthValidator(cfg),
		KeyLookup: "query:key",
	}
}
