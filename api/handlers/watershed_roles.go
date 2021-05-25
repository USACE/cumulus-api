package handlers

import (
	"net/http"

	"api/models"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v4/pgxpool"
	"github.com/labstack/echo/v4"
)

// ListWatershedRoles returns watershed Roles and their role information
func ListWatershedRoles(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		id, err := uuid.Parse(c.Param("watershed_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "Malformed ID")
		}
		mm, err := models.ListWatershedRoles(db, &id)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, err)
		}
		return c.JSON(http.StatusOK, mm)
	}
}

func AddWatershedRole(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {

		watershedID, err := uuid.Parse(c.Param("watershed_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "Malformed ID")
		}
		profileID, err := uuid.Parse(c.Param("profile_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "Malformed ID")
		}
		roleID, err := uuid.Parse(c.Param("role_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "Malformed ID")
		}

		// profile granting role to profile_id
		grantedBy := c.Get("profile").(*models.Profile)

		r, err := models.AddWatershedRole(db, &watershedID, &profileID, &roleID, &grantedBy.ID)

		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, r)
	}
}

func RemoveWatershedRole(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {

		watershedID, err := uuid.Parse(c.Param("watershed_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "Malformed ID")
		}
		profileID, err := uuid.Parse(c.Param("profile_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "Malformed ID")
		}
		roleID, err := uuid.Parse(c.Param("role_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "Malformed ID")
		}

		if err := models.RemoveWatershedRole(db, &watershedID, &profileID, &roleID); err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, make(map[string]interface{}))
	}
}
