package handlers

import (
	"api/models"
	"net/http"

	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	"github.com/labstack/echo/v4"
)

// ListWatershedAreaGroups lists all area groups for a watershed
func ListWatershedAreaGroups(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Get Watershed ID
		watershedID, err := uuid.Parse(c.Param("watershed_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		gg, err := models.ListWatershedAreaGroups(db, &watershedID)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, &gg)
	}
}

// ListAreaGroupAreas returns all areas for an area group
func ListAreaGroupAreas(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Get Area Group ID
		areaGroupID, err := uuid.Parse(c.Param("area_group_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		aa, err := models.ListAreaGroupAreas(db, &areaGroupID)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, &aa)
	}
}

// EnableAreaGroupProductStatistics enables statistics for a product for an area group
func EnableAreaGroupProductStatistics(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Get Area Group ID
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
		// Get Area Group ID
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
