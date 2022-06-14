package middleware

import "github.com/labstack/echo/v4"

// urlSkipper middleware ignores metrics on some route
var MetricsUrlSkipper = func(c echo.Context) bool {
	return c.Path() == "/*"
}
