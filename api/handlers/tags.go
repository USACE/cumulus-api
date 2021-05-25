package handlers

import (
	"net/http"

	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"

	"api/models"

	"github.com/jackc/pgx/v4/pgxpool"
)

// ListProducts returns a list of all products
func ListTags(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		tt, err := models.ListTags(db)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, tt)
	}
}

func CreateTag(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		var t models.Tag
		if err := c.Bind(&t); err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		newTag, err := models.CreateTag(db, &t)
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		return c.JSON(http.StatusCreated, newTag)
	}
}

func GetTag(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		tagID, err := uuid.Parse(c.Param("tag_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		t, err := models.GetTag(db, &tagID)
		if err != nil {
			if pgxscan.NotFound(err) {
				return c.JSON(http.StatusNotFound, models.DefaultMessageNotFound)
			}
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, t)
	}
}

func UpdateTag(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Tag ID From Route Params
		tagID, err := uuid.Parse(c.Param("tag_id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		// Tag ID From Payload
		var t models.Tag
		if err := c.Bind(&t); err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		if tagID != t.ID {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		tUpdated, err := models.UpdateTag(db, &t)
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, tUpdated)
	}
}

func DeleteTag(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		tagID, err := uuid.Parse(c.Param("tag_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		if err := models.DeleteTag(db, &tagID); err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, make(map[string]interface{}))
	}
}
