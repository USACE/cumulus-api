package handlers

import (
	"api/models"
	"net/http"

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
		// Profile Always Attached in Middleware for Private Routes
		p, ok := c.Get("profile").(*models.Profile)
		if !ok {
			return c.JSON(http.StatusNotFound, models.DefaultMessageNotFound)
		}
		return c.JSON(http.StatusOK, &p)
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
