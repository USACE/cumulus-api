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
		p := c.Request().URL.Path
		// Skip GZIP compression for COG byte-range streaming, where compression
		// breaks Range / Content-Length / Content-Range semantics.
		return strings.Contains(p, "/cog/")
	},
})
