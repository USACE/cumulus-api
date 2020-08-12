package handlers

import (
	"api/root/models"
	"net/http"

	"github.com/jmoiron/sqlx"
	"github.com/labstack/echo"
)

// ListDownloads returns an array of Basin
func ListDownloads(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		dd, err := models.ListDownloads(db)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, dd)
	}
}
