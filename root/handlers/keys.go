package handlers

import (
	"api/root/models"
	"api/root/passwords"
	"net/http"

	"github.com/jmoiron/sqlx"
	"github.com/labstack/echo/v4"
)

// CreateKey returns a key
func CreateKey(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {

		secretKey := passwords.GenerateRandom(40)
		keyID := passwords.GenerateRandom(40)

		// Generate Key Hash
		hash := passwords.MustCreateHash(secretKey, passwords.DefaultParams)

		// Save Key Hash to Database
		if _, err := models.CreateKeyInfo(db, &keyID, &hash); err != nil {
			return c.JSON(http.StatusBadRequest, err)
		}

		return c.JSON(http.StatusCreated, map[string]interface{}{
			"key_id": keyID,
			"key":    secretKey,
		})
	}
}
