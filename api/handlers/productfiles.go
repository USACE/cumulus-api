package handlers

import (
	"context"
	"fmt"
	"net/http"
	"time"

	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"

	"github.com/USACE/cumulus-api/api/models"

	_ "github.com/jackc/pgx/v4"
	"github.com/jackc/pgx/v4/pgxpool"
)

var minResolutionSql = `SELECT min(p.temporal_resolution) as temporal_resolution 
						FROM product p
						WHERE p.product_series_id = $1`

// ListProductFiles returns an array of Productfiles for a product
func ListProductFiles(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// uuid
		id, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "Malformed ID")
		}
		// after
		after := c.QueryParam("after")
		// before
		before := c.QueryParam("before")

		if after == "" || before == "" {
			return c.String(
				http.StatusBadRequest,
				"Missing query parameter 'after' or 'before'",
			)
		}

		ff, err := models.ListProductFiles(db, id, after, before)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}

		return c.JSON(http.StatusOK, ff)
	}
}

// ListProductSeriesFiles returns an array of Productfiles for a product series
func ListProductSeriesFiles(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// uuid
		id, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "Malformed ID")
		}
		// after
		after := c.QueryParam("after")
		// before
		before := c.QueryParam("before")

		if after == "" || before == "" {
			return c.String(
				http.StatusBadRequest,
				"Missing query parameter 'after' or 'before'",
			)
		}

		ff, err := models.ListProductSeriesFiles(db, id, after, before)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}

		return c.JSON(http.StatusOK, ff)
	}
}

// GetProductFileAvailability returns an object denoting which timestamps for the product have files
func GetProductFileAvailability(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		id, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		product, err := models.GetProduct(db, &id)
		if err != nil {
			if pgxscan.NotFound(err) {
				return c.JSON(http.StatusNotFound, models.DefaultMessageNotFound)
			}
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)

		}
		d, err := time.Parse(time.RFC3339, c.QueryParam("date"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		interval := fmt.Sprint(product.TemporalResolution/60/60, " Hour")
		availability, err := models.GetProductFileAvailability(db, id, interval, d)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, availability)
	}
}

// GetProductSeriesFileAvailability returns an object denoting which timestamps for the product series have files
//
// NOTE: This currently uses the minimum temporal resolution for associated products.  An "ideal" implementation
// would adjust the interval dynamically based on the available products, but requires specific design on the
// UI side.
func GetProductSeriesFileAvailability(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		id, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		d, err := time.Parse(time.RFC3339, c.QueryParam("date"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		var minResolution int
		if err := pgxscan.Get(context.Background(), db, &minResolution, minResolutionSql, id); err != nil {
			return c.JSON(http.StatusInternalServerError, models.Message{Message: err.Error()})
		}
		interval := fmt.Sprint(minResolution/60/60, " Hour")
		availability, err := models.GetProductSeriesFileAvailability(db, id, interval, d)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, availability)
	}
}

// CreateProductfiles creates productfiles from an array of Productfiles
func CreateProductfiles(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		var ff []models.Productfile
		if err := c.Bind(&ff); err != nil {
			return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
		}
		savedCount, err := models.CreateProductfiles(db, ff)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
		}
		return c.JSON(http.StatusCreated, map[string]int{"productfiles_saved": savedCount})
	}
}
