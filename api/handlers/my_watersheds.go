package handlers

import (
	"net/http"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v4/pgxpool"
	"github.com/labstack/echo/v4"

	"github.com/USACE/cumulus-api/api/models"
)

// ListMyWatersheds returns a list of watersheds linked to the logged-in profile
func ListMyWatersheds(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		p, ok := c.Get("profile").(*models.Profile)
		if !ok {
			return c.JSON(http.StatusUnauthorized, models.DefaultMessageUnauthorized)
		}
		ww, err := models.ListMyWatersheds(db, &p.ID)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, err)
		}
		return c.JSON(http.StatusOK, ww)
	}
}

// MyWatershedsAdd links a watershed to logged-in profile
func MyWatershedsAdd(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		p, ok := c.Get("profile").(*models.Profile)
		if !ok {
			return c.JSON(http.StatusUnauthorized, models.DefaultMessageUnauthorized)
		}
		// Watershed ID From URL
		watershedID, err := uuid.Parse(c.Param("watershed_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, err)
		}
		if err := models.MyWatershedsAdd(db, &p.ID, &watershedID); err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, make(map[string]interface{}))
	}
}

// MyWatershedsRemove links a watershed to logged-in profile
func MyWatershedsRemove(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		p, ok := c.Get("profile").(*models.Profile)
		if !ok {
			return c.JSON(http.StatusUnauthorized, models.DefaultMessageUnauthorized)
		}
		// Watershed ID From URL
		watershedID, err := uuid.Parse(c.Param("watershed_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, err)
		}
		if err = models.MyWatershedsRemove(db, &p.ID, &watershedID); err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, make(map[string]interface{}))
	}
}
