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

func EnableBasinProductStatistics(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Get Basin ID
		basinID, err := uuid.Parse(c.Param("basin_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		// Get Product ID
		productID, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		if err := models.EnableBasinProductStatistics(db, &basinID, &productID); err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusCreated, make(map[string]interface{}))
	}
}

func DisableBasinProductStatistics(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Get Basin ID
		basinID, err := uuid.Parse(c.Param("basin_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		// Get Product ID
		productID, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		if err := models.DisableBasinProductStatistics(db, &basinID, &productID); err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, make(map[string]interface{}))
	}
}
