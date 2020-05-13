package handlers

import (
	"api/root/models"
	"api/root/passwords"
	"net/http"

	"github.com/jmoiron/sqlx"
	"github.com/labstack/echo"
)

// CreateToken returns a token
func CreateToken(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {

		// Generate New Token
		t := models.Token{
			SecretKey: passwords.GenerateToken(),
		}

		// Generate Token Hash
		hash := passwords.MustCreateHash(t.SecretKey, passwords.DefaultParams)

		// Save Token Hash to Database
		if err := models.CreateTokenHash(db, &hash); err != nil {
			return c.JSON(http.StatusBadRequest, err)
		}

		return c.JSON(http.StatusCreated, t)
	}
}
