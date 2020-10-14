package handlers

import (
	"net/http"

	"github.com/jmoiron/sqlx"
	"github.com/labstack/echo"

	"api/root/models"

	"github.com/USACE/go-simple-asyncer/asyncer"

	// SQL Interface
	_ "github.com/lib/pq"
)

// CreateAcquisitionAttempt creates an acquisition record and fires acquisition events
func CreateAcquisitionAttempt(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		acquisition, err := models.CreateAcquisitionAttempt(db)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, err)
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
		return c.JSON(http.StatusCreated, &acquisition)
	}
}

// ListAcquirableInfo lists all acquirables
func ListAcquirableInfo(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		aa, err := models.ListAcquirableInfo(db)
		if err != nil {
			return c.JSON(http.StatusBadRequest, err)
		}
		return c.JSON(http.StatusOK, aa)
	}
}
