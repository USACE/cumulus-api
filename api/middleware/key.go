package middleware

import (
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

// KeyAuth returns a ready-to-go key auth middleware
func KeyAuth(isDisabled bool, appKey string) echo.MiddlewareFunc {
	return middleware.KeyAuthWithConfig(
		middleware.KeyAuthConfig{
			// If Auth Manually Disabled via Environment Variable
			// or "?key=..." is not in QueryParams (counting on other auth middleware
			// further down the chain); Skip this middleware
			Skipper: func(c echo.Context) bool {
				if isDisabled || c.QueryParam("key") == "" {
					return true
				}
				return false
			},
			// Compare key passed via query parameters with hash stored in the database
			Validator: func(key string, c echo.Context) (bool, error) {
				// If Key is Master ApplicationKey; Grant Access
				////////////////////////////////////////////////
				if key == appKey {
					c.Set("ApplicationKeyAuthSuccess", true)
					return true, nil
				}
				return false, nil
			},
			KeyLookup: "query:key",
		},
	)
}
