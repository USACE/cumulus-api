package handlers

import (
	"net/http"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v4/pgxpool"
	"github.com/labstack/echo/v4"

	"github.com/USACE/cumulus-api/api/models"
)

// ListMyWatersheds returns a list of watersheds linked to the logged-in sub
func ListMyWatersheds(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		sub, err := GetSub(c)
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageUnauthorized)
		}
		ww, err := models.ListMyWatersheds(db, sub)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, err)
		}
		return c.JSON(http.StatusOK, ww)
	}
}

// MyWatershedsAdd links a watershed to logged-in sub
func MyWatershedsAdd(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		sub, err := GetSub(c)
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageUnauthorized)
		}
		// Watershed ID From URL
		watershedID, err := uuid.Parse(c.Param("watershed_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, err)
		}
		if err := models.MyWatershedsAdd(db, sub, &watershedID); err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, make(map[string]interface{}))
	}
}

// MyWatershedsRemove links a watershed to sub
func MyWatershedsRemove(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		sub, err := GetSub(c)
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageUnauthorized)
		}
		// Watershed ID From URL
		watershedID, err := uuid.Parse(c.Param("watershed_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, err)
		}
		if err = models.MyWatershedsRemove(db, sub, &watershedID); err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, make(map[string]interface{}))
	}
}
