package handlers

import (
	"net/http"

	"github.com/labstack/echo/v4"

	"github.com/USACE/cumulus-api/api/models"

	"github.com/jackc/pgx/v4/pgxpool"
)

// ListDssDatatypes returns a list of all parameters
func ListDssDatatypes(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		dd, err := models.ListDssDatatypes(db)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, dd)
	}
}
