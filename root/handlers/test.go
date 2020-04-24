package handlers

import (
	"net/http"

	"github.com/labstack/echo"
)

// GetTest returns a test endpoint to make sure everything is working
func GetTest(c echo.Context) error {
	return c.String(http.StatusOK, "Test Endpoint for Cumulus API")
}
