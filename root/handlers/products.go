package handlers

import (
	"net/http"

	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	"github.com/labstack/echo"

	"api/root/models"

	_ "github.com/lib/pq"
)

// ListProducts returns a list of all products
func ListProducts(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		return c.JSON(http.StatusOK, models.ListProducts(db))
	}
}

// GetProduct returns a single Product
func GetProduct(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		id, err := uuid.Parse(c.Param("id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "Malformed ID")
		}
		return c.JSON(http.StatusOK, models.GetProduct(db, id))
	}
}

// GetProductProductfiles returns an array of Productfiles
func GetProductProductfiles(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		// uuid
		id, err := uuid.Parse(c.Param("id"))
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

		return c.JSON(
			http.StatusOK,
			models.GetProductProductfiles(db, id, after, before),
		)
	}
}

// ListProductsAcquirable returns a list of all acquirable products
func ListProductsAcquirable(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		productsAcquirable, err := models.ListProductsAcquirable(db)
		if err != nil {
			return c.NoContent(http.StatusInternalServerError)
		}
		return c.JSON(http.StatusOK, productsAcquirable)
	}
}
