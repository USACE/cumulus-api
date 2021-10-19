package handlers

import (
	"net/http"

	"github.com/USACE/cumulus-api/api/models"

	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v4/pgxpool"
	"github.com/labstack/echo/v4"
)

// CreateProfile creates a user profile
func CreateProfile(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Attach EDIPI
		edipi, ok := c.Get("EDIPI").(int)
		if !ok {
			return c.JSON(http.StatusUnauthorized, models.DefaultMessageUnauthorized)
		}
		// Get info to create profile
		var n models.ProfileInfo
		if err := c.Bind(&n); err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		// Set EDIPI from JWT that authorized request
		n.EDIPI = edipi

		p, err := models.CreateProfile(db, &n)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusCreated, p)
	}
}

// GetMyProfile returns profile for current authenticated user or 404
func GetMyProfile(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		edipi, ok := c.Get("EDIPI").(int)
		if !ok {
			return c.JSON(http.StatusUnauthorized, models.DefaultMessageUnauthorized)
		}
		p, err := models.GetProfileFromEDIPI(db, edipi)
		if err != nil {
			if pgxscan.NotFound(err) {
				return c.JSON(http.StatusNotFound, models.DefaultMessageNotFound)
			}
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, p)
	}
}

// CreateToken returns a list of all products
func CreateToken(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		EDIPI := c.Get("EDIPI").(int)
		p, err := models.GetProfileFromEDIPI(db, EDIPI)
		if err != nil {
			return c.String(
				http.StatusBadRequest,
				"could not locate user profile with information provided",
			)
		}
		token, err := models.CreateProfileToken(db, &p.ID)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusCreated, token)
	}
}

// DeleteToken deletes a token
func DeleteToken(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Get Profile ID Used to make the request
		p, ok := c.Get("profile").(*models.Profile)
		if !ok {
			return c.JSON(http.StatusUnauthorized, models.DefaultMessageUnauthorized)
		}
		// Get Token ID
		tokenID := c.Param("token_id")
		if tokenID == "" {
			return c.String(http.StatusBadRequest, "Bad Token ID")
		}
		// Delete Token
		if err := models.DeleteToken(db, &p.ID, &tokenID); err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, make(map[string]interface{}))
	}
}

// GrantApplicationAdmin grants Admin to a user
func GrantApplicationAdmin(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		pID, err := uuid.Parse(c.Param("profile_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		if err := models.GrantApplicationAdmin(db, &pID); err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, make(map[string]interface{}))
	}
}

// RevokeApplicationAdmin Revokes Admin from a user
func RevokeApplicationAdmin(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		pID, err := uuid.Parse(c.Param("profile_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		if err := models.RevokeApplicationAdmin(db, &pID); err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, make(map[string]interface{}))
	}
}
