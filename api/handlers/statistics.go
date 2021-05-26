package handlers

import (
	"net/http"

	"github.com/jmoiron/sqlx"
	"github.com/labstack/echo/v4"

	"api/models"

	"github.com/USACE/go-simple-asyncer/asyncer"

	// SQL Interface
	_ "github.com/jackc/pgx/v4"
)

// DoStatistics triggers statistics
func DoStatistics(db *sqlx.DB, ae asyncer.Asyncer) echo.HandlerFunc {
	return func(c echo.Context) error {
		err := models.DoStatistics(db, ae)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.NoContent(http.StatusCreated)
	}
}
