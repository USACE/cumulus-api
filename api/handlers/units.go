package handlers

import (
	"net/http"

	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"

	"github.com/USACE/cumulus-api/api/models"

	"github.com/jackc/pgx/v4/pgxpool"
)

// ListUnits returns a list of all products
func ListUnits(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		tt, err := models.ListUnits(db)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, tt)
	}
}

func CreateUnit(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		var t models.Unit
		if err := c.Bind(&t); err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		newUnit, err := models.CreateUnit(db, &t)
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		return c.JSON(http.StatusCreated, newUnit)
	}
}

func GetUnit(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		unitID, err := uuid.Parse(c.Param("unit_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		u, err := models.GetUnit(db, &unitID)
		if err != nil {
			if pgxscan.NotFound(err) {
				return c.JSON(http.StatusNotFound, models.DefaultMessageNotFound)
			}
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, u)
	}
}

func UpdateUnit(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Unit ID From Route Params
		unitID, err := uuid.Parse(c.Param("unit_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		// Unit ID From Payload
		var u models.Unit
		if err := c.Bind(&u); err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		if unitID != u.ID {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		uUpdated, err := models.UpdateUnit(db, &u)
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, uUpdated)
	}
}

func DeleteUnit(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		unitID, err := uuid.Parse(c.Param("unit_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		if err := models.DeleteUnit(db, &unitID); err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, make(map[string]interface{}))
	}
}
