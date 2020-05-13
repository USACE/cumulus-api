package appconfig

import (
	"api/root/models"
	"api/root/passwords"
	"log"

	"github.com/labstack/echo"
	"github.com/labstack/echo/middleware"
)

func keyAuthValidator(cfg *Config) middleware.KeyAuthValidator {
	return func(key string, c echo.Context) (bool, error) {
		log.Printf("Received Token from URL: %s", key)

		db := Connection(cfg)

		// Get hash from database
		hashes, err := models.ListTokenHashes(db)
		if err != nil {
			log.Printf(err.Error())
			return false, err
		}

		// Check if token matches a valid hash in the database
		for _, hash := range hashes {
			match, err := passwords.ComparePasswordAndHash(key, hash.Hash)
			if err != nil {
				log.Printf(err.Error())
				return false, err
			}
			if match && !hash.Revoked {
				log.Print("VALID TOKEN!")
				return true, nil
			}
		}

		log.Printf("Invalid Token")

		return false, nil
	}
}

func keyAuthSkipper(cfg *Config) middleware.Skipper {
	return func(c echo.Context) bool {

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
func KeyAuthConfig(cfg *Config) *middleware.KeyAuthConfig {
	return &middleware.KeyAuthConfig{
		Skipper:   keyAuthSkipper(cfg),
		Validator: keyAuthValidator(cfg),
		KeyLookup: "query:token",
	}
}
