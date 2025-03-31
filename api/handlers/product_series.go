package handlers

import (
	"net/http"

	"github.com/georgysavva/scany/pgxscan"
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

// GetProductSeriesIngestStatus returns a list of product series status
func GetProductSeriesIngestStatus(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {

		productStatus, err := models.GetProductSeriesIngestStatus(db)
		if err != nil {
			if pgxscan.NotFound(err) {
				return c.JSON(http.StatusNotFound, models.DefaultMessageNotFound)
			}
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, productStatus)
	}
}

// GetProductSeriesSlugs returns a map of slug: id for all product series
func GetProductSeriesSlugs(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		m, err := models.GetProductSeriesSlugs(db)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, m)
	}
}
