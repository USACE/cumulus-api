package appconfig

import (
	"api/root/models"
	"api/root/passwords"

	"github.com/labstack/echo"
	"github.com/labstack/echo/middleware"
)

func keyAuthValidator() middleware.KeyAuthValidator {
	return func(key string, c echo.Context) (bool, error) {

		// Get hash from database
		hashes, err := models.ListTokenHashes(Connection())
		if err != nil {
			return false, err
		}

		// Check if token matches a valid hash in the database
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

func keyAuthSkipper() middleware.Skipper {
	return func(c echo.Context) bool {
		cfg := AppConfig()
		if cfg.KeyAuthDisabled {
			return true
		}
		// If JWT is not disabled and token is not in querystring
		if !cfg.JWTAuthDisabled && c.QueryParam("token") == "" {
			return true
		}
		return false
	}
}

// KeyAuthConfig supports Key-Based Authentication for the API
func KeyAuthConfig() *middleware.KeyAuthConfig {
	return &middleware.KeyAuthConfig{
		Skipper:   keyAuthSkipper(),
		Validator: keyAuthValidator(),
		KeyLookup: "query:token",
	}
}
