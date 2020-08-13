package handlers

import (
	"api/root/models"
	"net/http"

	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	"github.com/labstack/echo"
)

// ListDownloads returns an array of download requests
func ListDownloads(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		dd, err := models.ListDownloads(db)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, dd)
	}
}

// Create download request, return dummy response for testing until
// dss processing/file creation is available
func CreateDownload(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		//need to check if products provided are valid uuids for existing products
		//sanity check on dates in time windows and geometry??

		dd, err := models.CreateDownload(db)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, dd)
	}
}

func GetDownload(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {

		downloadID, err := uuid.Parse(c.Param("id"))
		if err != nil {
			//return c.String(http.StatusBadRequest, "Malformed ID")
			return c.String(http.StatusBadRequest, err.Error())
		}
		dl, err := models.GetDownload(db, &downloadID)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, dl)
	}
}
