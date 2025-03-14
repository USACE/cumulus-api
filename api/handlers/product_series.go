package handlers

import (
	"net/http"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"

	"github.com/USACE/cumulus-api/api/models"

	_ "github.com/jackc/pgx/v4"
	"github.com/jackc/pgx/v4/pgxpool"
)

// ListProductSeries returns a list of all product series
func ListProductSeries(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		products, err := models.ListProductSeries(db)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, products)
	}
}

// GetProductSeriesAvailability returns an Availability object
func GetProductSeriesAvailability(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {

		// uuid
		id, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "Malformed ID")
		}
		a, err := models.GetProductSeriesAvailability(db, &id)
		if err != nil {
			return c.JSON(http.StatusBadRequest, err.Error())
		}
		return c.JSON(http.StatusOK, a)
	}
}
