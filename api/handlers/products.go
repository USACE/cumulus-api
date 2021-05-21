package handlers

import (
	"net/http"

	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"

	"api/models"

	_ "github.com/jackc/pgx/v4"
	"github.com/jackc/pgx/v4/pgxpool"
)

// ListProducts returns a list of all products
func ListProducts(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		products, err := models.ListProducts(db)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, products)
	}
}

// GetProduct returns a single Product
func GetProduct(db *pgxpool.Pool) echo.HandlerFunc {
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
		return c.JSON(http.StatusOK, product)
	}
}

// CreateProduct creates a single new product
func CreateProduct(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		var n models.ProductInfo
		if err := c.Bind(&n); err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		pNew, err := models.CreateProduct(db, &n)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusCreated, &pNew)

	}
}

// UpdateProduct updates a single product
func UpdateProduct(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Product ID from Route Params
		pID, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "Malformed ID")
		}
		// Product ID from Payload
		var p models.Product
		if err := c.Bind(&p); err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		// Compare Product ID from Route Params to Product ID from Payload
		if pID != p.ID {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		pUpdated, err := models.UpdateProduct(db, &p)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, pUpdated)
	}
}

// DeleteProduct deletes a single product
func DeleteProduct(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Product ID from Route Params
		pID, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "Malformed ID")
		}
		if err := models.DeleteProduct(db, &pID); err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, make(map[string]interface{}))
	}
}

// UndeleteProduct un-deletes a single product
func UndeleteProduct(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Product ID from Route Params
		pID, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		p, err := models.UndeleteProduct(db, &pID)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, p)
	}
}

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

// GetProductAvailability returns an availability object
func GetProductAvailability(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {

		// uuid
		id, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "Malformed ID")
		}
		a, err := models.GetProductAvailability(db, &id)
		if err != nil {
			return c.JSON(http.StatusBadRequest, err.Error())
		}
		return c.JSON(http.StatusOK, a)
	}
}

func TagProduct(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Product ID
		pID, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		// Tag ID
		tID, err := uuid.Parse(c.Param("tag_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		// Tag Product
		p, err := models.TagProduct(db, &pID, &tID)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, &p)
	}
}

func UntagProduct(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Product ID
		pID, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		// Tag ID
		tID, err := uuid.Parse(c.Param("tag_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		// Tag Product
		p, err := models.UntagProduct(db, &pID, &tID)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, &p)
	}
}
