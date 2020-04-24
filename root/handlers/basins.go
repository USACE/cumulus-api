package handlers

import (
	"database/sql"
	"net/http"

	"github.com/google/uuid"
	"github.com/labstack/echo"

	"api/root/models"

	_ "github.com/lib/pq"
)

// ListBasins returns an array of Basin
func ListBasins(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		return c.JSON(http.StatusOK, models.ListBasins(db))
	}
}

// GetBasin returns a single Basin
func GetBasin(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		id, err := uuid.Parse(c.Param("id"))
		if err != nil {
			return c.String(http.StatusNotFound, "Malformed ID")
		}
		return c.JSON(http.StatusOK, models.GetBasin(db, id.String()))
	}
}
