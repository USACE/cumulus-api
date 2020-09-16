package middleware

import (
	"api/root/models"
	"api/root/passwords"

	"github.com/labstack/echo"
	"github.com/labstack/echo/middleware"
)

// KeyAuth returns a ready-to-go key auth middleware
func KeyAuth(isDisabled bool, validKeys []models.KeyInfo) echo.MiddlewareFunc {
	return middleware.KeyAuthWithConfig(
		middleware.KeyAuthConfig{
			// Skipper
			// If Auth Manually Disabled via Environment Variable
			// or "?key=..." is not in QueryParams, skip middleware
			Skipper: func(c echo.Context) bool {
				if isDisabled || c.QueryParam("key") == "" {
					return true
				}
				return false
			},
			// Compare key passed via query parameters with hash stored in the database
			Validator: func(key string, c echo.Context) (bool, error) {
				// Check if key matches a valid hash in the database
				for _, k := range validKeys {
					match, err := passwords.ComparePasswordAndHash(key, k.Hash)
					if err != nil {
						return false, err
					}
					if match && !k.Revoked {
						return true, nil
					}
				}
				return false, nil
			},
			KeyLookup: "query:key",
		},
	)
}
