package handlers

import (
	"net/http"

	"github.com/USACE/cumulus-api/api/models"
	"github.com/jackc/pgx/v4/pgxpool"
	"github.com/labstack/echo/v4"
)

// ListOffices returns a list of all parameters
func ListOffices(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		oo, err := models.ListOffices(db)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, oo)
	}
}
