package handlers

import (
	"net/http"

	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	"github.com/labstack/echo"

	"api/root/models"

	_ "github.com/lib/pq"
)

// ListBasins returns an array of Basin
func ListBasins(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		return c.JSON(http.StatusOK, models.ListBasins(db))
	}
}

// GetBasin returns a single Basin
func GetBasin(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		id, err := uuid.Parse(c.Param("id"))
		if err != nil {
			return c.NoContent(http.StatusNotFound)
		}
		return c.JSON(http.StatusOK, models.GetBasin(db, id))
	}
}
