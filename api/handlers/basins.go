package handlers

import (
	"net/http"
	"strings"

	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	"github.com/labstack/echo/v4"

	"api/models"

	_ "github.com/lib/pq"
)

// ListBasins returns an array of Basin
func ListBasins(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		return c.JSON(http.StatusOK, models.ListBasins(db))
	}
}

// ListOfficeBasins returns basins for an office based on office_slug in the route parameters
func ListOfficeBasins(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		officeSlug := strings.ToUpper(c.Param("office_slug"))
		bb, err := models.ListOfficeBasins(db, officeSlug)
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		return c.JSON(http.StatusOK, bb)
	}
}

// GetBasin returns a single Basin
func GetBasin(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		id, err := uuid.Parse(c.Param("id"))
		if err != nil {
			return c.NoContent(http.StatusBadRequest)
		}
		b, err := models.GetBasin(db, &id)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, b)
	}
}
