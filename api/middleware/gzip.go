package middleware

import (
	"strings"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

// GZIP is ready-to-go GZIP middleware based on echo middleware
// GZIP is ready-to-go GZIP middleware with a skipper to exclude certain routes
var GZIP = middleware.GzipWithConfig(middleware.GzipConfig{
	Level: 5,
	Skipper: func(c echo.Context) bool {
		// Skip GZIP compression for routes starting with /features
		// as compression messes with pg_featureserv
		return strings.Contains(c.Request().URL.Path, "/features")
	},
})
