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

// GetProduct returns a single Product
func GetProductSeries(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		id, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		product, err := models.GetProductSeries(db, &id)
		if err != nil {
			if pgxscan.NotFound(err) {
				return c.JSON(http.StatusNotFound, models.DefaultMessageNotFound)
			}
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, product)
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

// CreateProductSeries creates a single new product series
func CreateProductSeries(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		var n models.ProductSeriesInfo
		if err := c.Bind(&n); err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		pNew, err := models.CreateProductSeries(db, &n)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusCreated, &pNew)

	}
}

// UpdateProductSeries updates a single product series
func UpdateProductSeries(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Product Series ID from Route Params
		pID, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "Malformed ID")
		}
		// Product Series ID from Payload
		var p models.ProductSeries
		if err := c.Bind(&p); err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		// Compare Product Series ID from Route Params to Product Series ID from Payload
		if pID != p.ID {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		pUpdated, err := models.UpdateProductSeries(db, &p)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, pUpdated)
	}
}

// DeleteProductSeries deletes a single product series
func DeleteProductSeries(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Product Series ID from Route Params
		pID, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "Malformed ID")
		}
		if err := models.DeleteProductSeries(db, &pID); err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, make(map[string]interface{}))
	}
}

// UndeleteProduct un-deletes a single product series
func UndeleteProductSeries(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Product Series ID from Route Params
		pID, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		p, err := models.UndeleteProductSeries(db, &pID)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, p)
	}
}
