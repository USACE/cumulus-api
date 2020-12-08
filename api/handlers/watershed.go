package handlers

import (
	"net/http"

	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	"github.com/labstack/echo/v4"

	"api/models"

	_ "github.com/lib/pq"
)

// ListWatersheds returns an array of Watersheds
func ListWatersheds(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		ww, err := models.ListWatersheds(db)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, ww)
	}
}

// GetWatershed returns a single Watershed
func GetWatershed(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		id, err := uuid.Parse(c.Param("watershed_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		w, err := models.GetWatershed(db, &id)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, w)
	}
}

// CreateWatershed creates a new watershed
func CreateWatershed(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		var w models.Watershed
		if err := c.Bind(&w); err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		newWatershed, err := models.CreateWatershed(db, &w)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusCreated, newWatershed)
	}
}

// UpdateWatershed creates a new watershed
func UpdateWatershed(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Watershed Slug from route params
		id, err := uuid.Parse(c.Param("watershed_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		// Payload
		var w models.Watershed
		if err := c.Bind(&w); err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		// Check route params v. payload
		if id != w.ID {
			return c.String(http.StatusBadRequest, "watershed_id in URL does not match request body")
		}
		wUpdated, err := models.UpdateWatershed(db, &w)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusCreated, wUpdated)
	}
}

// DeleteWatershed creates a new watershed
func DeleteWatershed(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		id, err := uuid.Parse(c.Param("watershed_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		err = models.DeleteWatershed(db, &id)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, make(map[string]interface{}))
	}
}
