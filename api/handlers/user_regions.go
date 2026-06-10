package handlers

import (
	"net/http"

	"github.com/USACE/cumulus-api/api/messages"
	"github.com/USACE/cumulus-api/api/models"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"
)

// ListMyRegions returns all regions for the authenticated user
func ListMyRegions(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		sub, err := GetSub(c)
		if err != nil {
			return c.JSON(http.StatusUnauthorized, models.DefaultMessageUnauthorized)
		}

		regions, err := models.ListUserRegions(db, sub)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}

		return c.JSON(http.StatusOK, regions)
	}
}

// ListPublicRegions returns all public regions
func ListPublicRegions(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		regions, err := models.ListPublicUserRegions(db)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}

		return c.JSON(http.StatusOK, regions)
	}
}

// GetUserRegion returns a single user region
func GetUserRegion(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		sub, err := GetSub(c)
		if err != nil {
			return c.JSON(http.StatusUnauthorized, models.DefaultMessageUnauthorized)
		}

		regionID, err := uuid.Parse(c.Param("region_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, messages.NewMessage("Invalid region ID"))
		}

		region, err := models.GetUserRegion(db, &regionID, sub)
		if err != nil {
			if err == pgx.ErrNoRows {
				return c.JSON(http.StatusNotFound, messages.NewMessage("Region not found"))
			}
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}

		return c.JSON(http.StatusOK, region)
	}
}

// CreateUserRegion creates a new user region
func CreateUserRegion(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		sub, err := GetSub(c)
		if err != nil {
			return c.JSON(http.StatusUnauthorized, models.DefaultMessageUnauthorized)
		}

		var input models.UserRegionInput
		if err := c.Bind(&input); err != nil {
			return c.JSON(http.StatusBadRequest, messages.NewMessage("Invalid request body"))
		}

		// Validate the input
		if input.Name == "" {
			return c.JSON(http.StatusBadRequest, messages.NewMessage("Region name is required"))
		}

		if len(input.GeoJSON) == 0 {
			return c.JSON(http.StatusBadRequest, messages.NewMessage("GeoJSON is required"))
		}

		region, err := models.CreateUserRegion(db, sub, &input)
		if err != nil {
			// Check for unique constraint violation
			if err.Error() == "ERROR: duplicate key value violates unique constraint \"unique_user_region_name\" (SQLSTATE 23505)" {
				return c.JSON(http.StatusConflict, messages.NewMessage("A region with this name already exists"))
			}
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}

		return c.JSON(http.StatusCreated, region)
	}
}

// UpdateUserRegion updates an existing user region
func UpdateUserRegion(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		sub, err := GetSub(c)
		if err != nil {
			return c.JSON(http.StatusUnauthorized, models.DefaultMessageUnauthorized)
		}

		regionID, err := uuid.Parse(c.Param("region_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, messages.NewMessage("Invalid region ID"))
		}

		var input models.UserRegionInput
		if err := c.Bind(&input); err != nil {
			return c.JSON(http.StatusBadRequest, messages.NewMessage("Invalid request body"))
		}

		// Validate the input
		if input.Name == "" {
			return c.JSON(http.StatusBadRequest, messages.NewMessage("Region name is required"))
		}

		if len(input.GeoJSON) == 0 {
			return c.JSON(http.StatusBadRequest, messages.NewMessage("GeoJSON is required"))
		}

		region, err := models.UpdateUserRegion(db, &regionID, sub, &input)
		if err != nil {
			if err == pgx.ErrNoRows {
				return c.JSON(http.StatusNotFound, messages.NewMessage("Region not found or you don't have permission to update it"))
			}
			// Check for unique constraint violation
			if err.Error() == "ERROR: duplicate key value violates unique constraint \"unique_user_region_name\" (SQLSTATE 23505)" {
				return c.JSON(http.StatusConflict, messages.NewMessage("A region with this name already exists"))
			}
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}

		return c.JSON(http.StatusOK, region)
	}
}

// DeleteUserRegion deletes a user region
func DeleteUserRegion(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		sub, err := GetSub(c)
		if err != nil {
			return c.JSON(http.StatusUnauthorized, models.DefaultMessageUnauthorized)
		}

		regionID, err := uuid.Parse(c.Param("region_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, messages.NewMessage("Invalid region ID"))
		}

		err = models.DeleteUserRegion(db, &regionID, sub)
		if err != nil {
			if err == pgx.ErrNoRows {
				return c.JSON(http.StatusNotFound, messages.NewMessage("Region not found or you don't have permission to delete it"))
			}
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}

		return c.JSON(http.StatusNoContent, nil)
	}
}

// SearchUserRegions searches for regions by name or tags
func SearchUserRegions(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		sub, err := GetSub(c)
		if err != nil {
			return c.JSON(http.StatusUnauthorized, models.DefaultMessageUnauthorized)
		}

		query := c.QueryParam("q")
		if query == "" {
			return c.JSON(http.StatusBadRequest, messages.NewMessage("Search query is required"))
		}

		regions, err := models.SearchUserRegions(db, sub, query)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}

		return c.JSON(http.StatusOK, regions)
	}
}
