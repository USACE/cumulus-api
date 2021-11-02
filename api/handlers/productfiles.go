package handlers

import (
	"net/http"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"

	"github.com/USACE/cumulus-api/api/models"

	_ "github.com/jackc/pgx/v4"
	"github.com/jackc/pgx/v4/pgxpool"
)

// ListProductfiles returns an array of Productfiles
func ListProductfiles(db *pgxpool.Pool) echo.HandlerFunc {
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

		ff, err := models.ListProductfiles(db, id, after, before)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}

		return c.JSON(http.StatusOK, ff)
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