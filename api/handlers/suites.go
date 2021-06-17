package handlers

import (
	"net/http"

	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"

	"api/models"

	"github.com/jackc/pgx/v4/pgxpool"
)

// ListSuites returns a list of all product suites
func ListSuites(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		ss, err := models.ListSuites(db)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, ss)
	}
}

func CreateSuite(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		var s models.Suite
		if err := c.Bind(&s); err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		newSuite, err := models.CreateSuite(db, &s)
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		return c.JSON(http.StatusCreated, newSuite)
	}
}

func GetSuite(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		suiteID, err := uuid.Parse(c.Param("suite_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		s, err := models.GetSuite(db, &suiteID)
		if err != nil {
			if pgxscan.NotFound(err) {
				return c.JSON(http.StatusNotFound, models.DefaultMessageNotFound)
			}
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, s)
	}
}

func UpdateSuite(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Suite ID From Route Params
		suiteID, err := uuid.Parse(c.Param("suite_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		// Suite ID From Payload
		var s models.Suite
		if err := c.Bind(&s); err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		if suiteID != s.ID {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		sUpdated, err := models.UpdateSuite(db, &s)
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, sUpdated)
	}
}

func DeleteSuite(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		suiteID, err := uuid.Parse(c.Param("suite_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		if err := models.DeleteSuite(db, &suiteID); err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, make(map[string]interface{}))
	}
}
