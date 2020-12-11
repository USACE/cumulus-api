package handlers

import (
	"api/models"
	"net/http"

	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	"github.com/labstack/echo/v4"
)

// EnableAreaGroupProductStatistics enables statistics for a product for an area group
func EnableAreaGroupProductStatistics(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Get Basin ID
		areaGroupID, err := uuid.Parse(c.Param("area_group_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		// Get Product ID
		productID, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		if err := models.EnableAreaGroupProductStatistics(db, &areaGroupID, &productID); err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, make(map[string]interface{}))
	}
}

// DisableAreaGroupProductStatistics disables statistics for a product for an area group
func DisableAreaGroupProductStatistics(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Get Basin ID
		areaGroupID, err := uuid.Parse(c.Param("area_group_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		// Get Product ID
		productID, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		if err := models.DisableAreaGroupProductStatistics(db, &areaGroupID, &productID); err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, make(map[string]interface{}))
	}
}
