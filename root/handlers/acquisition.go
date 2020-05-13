package handlers

import (
	"net/http"

	"github.com/jmoiron/sqlx"
	"github.com/labstack/echo"

	"api/root/asyncer"
	"api/root/models"

	// SQL Interface
	_ "github.com/lib/pq"
)

// CreateAcquisition creates an acquisition record and fires acquisition events
func CreateAcquisition(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		acquisition, err := models.CreateAcquisition(db)
		if err != nil {
			return c.NoContent(http.StatusInternalServerError)
		}
		return c.JSON(http.StatusCreated, acquisition)
	}
}

// DoAcquire triggers data acquisition for all acquirables in the database
func DoAcquire(db *sqlx.DB, ae asyncer.Asyncer) echo.HandlerFunc {
	return func(c echo.Context) error {
		acquisition, err := models.DoAcquire(db, ae)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, err)
		}
		return c.JSON(http.StatusCreated, acquisition)
	}
}

// ListAcquirables lists all acquirables
func ListAcquirables(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		aa, err := models.ListAcquirables(db)
		if err != nil {
			return c.JSON(http.StatusBadRequest, err)
		}
		return c.JSON(http.StatusOK, aa)
	}
}
