package handlers

import (
	"net/http"

	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"

	"api/models"

	"github.com/jackc/pgx/v4/pgxpool"
)

// ListParameters returns a list of all parameters
func ListParameters(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		pp, err := models.ListParameters(db)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, pp)
	}
}

func CreateParameter(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		var p models.Parameter
		if err := c.Bind(&p); err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		newParameter, err := models.CreateParameter(db, &p)
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		return c.JSON(http.StatusCreated, newParameter)
	}
}

func GetParameter(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		parameterID, err := uuid.Parse(c.Param("parameter_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		p, err := models.GetParameter(db, &parameterID)
		if err != nil {
			if pgxscan.NotFound(err) {
				return c.JSON(http.StatusNotFound, models.DefaultMessageNotFound)
			}
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, p)
	}
}

func UpdateParameter(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Parameter ID From Route Params
		parameterID, err := uuid.Parse(c.Param("parameter_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		// Parameter ID From Payload
		var p models.Parameter
		if err := c.Bind(&p); err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		if parameterID != p.ID {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		pUpdated, err := models.UpdateParameter(db, &p)
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, pUpdated)
	}
}

func DeleteParameter(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		parameterID, err := uuid.Parse(c.Param("parameter_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		if err := models.DeleteParameter(db, &parameterID); err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, make(map[string]interface{}))
	}
}
