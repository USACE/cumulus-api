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
			Token: passwords.GenerateToken(),
		}

		// Generate Token Hash
		t.ID = passwords.MustCreateHash(t.Token, passwords.DefaultParams)

		// Save Token Hash to Database
		if err := models.CreateTokenHash(db, &t.ID); err != nil {
			return c.NoContent(http.StatusBadRequest)
		}

		return c.JSON(http.StatusCreated, t)
	}
}
