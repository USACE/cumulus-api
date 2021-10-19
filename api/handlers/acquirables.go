package handlers

import (
	"net/http"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v4/pgxpool"
	"github.com/labstack/echo/v4"

	// SQL Interface
	_ "github.com/jackc/pgx/v4"

	"github.com/USACE/cumulus-api/api/models"
)

// ListAcquirable lists all acquirables
func ListAcquirables(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		aa, err := models.ListAcquirables(db)
		if err != nil {
			return c.JSON(http.StatusBadRequest, err)
		}
		return c.JSON(http.StatusOK, aa)
	}
}

// ListAcquirablefiles returns an array of Acquirablefiles
func ListAcquirablefiles(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// uuid
		id, err := uuid.Parse(c.Param("acquirable_id"))
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
		// Call the model, verify return value
		aa, err := models.ListAcquirablefiles(db, id, after, before)

		// handle any error from model
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		//otherwise return valid response from model above
		return c.JSON(http.StatusOK, aa)
	}
}

func CreateAcquirablefiles(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {

		//Get this payload and 400 if bad request
		var a models.Acquirablefile
		if err := c.Bind(&a); err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
			// return c.String(http.StatusBadRequest, err.Error())

		}

		//Save acquirablefile to database, 500 if internal server error
		aNew, err := models.CreateAcquirablefiles(db, a)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}

		//Return payload response
		return c.JSON(http.StatusCreated, aNew)
	}
}
