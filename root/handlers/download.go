package handlers

import (
	"api/root/models"
	"net/http"

	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	"github.com/labstack/echo"
)

/*
****************************
Example POST JSON BODY
****************************
{
	"datetime_start": "2020-08-15T00:00:00Z",
	"datetime_end": "2020-08-17T00:00:00Z",
	"product_id": [
		"e0baa220-1310-445b-816b-6887465cc94b",
		"757c809c-dda0-412b-9831-cb9bd0f62d1d"
	]
}
*/

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

// CreateDownload request, return dummy response for testing until
// dss processing/file creation is available
func CreateDownload(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		//need to check if products provided are valid uuids for existing products
		//sanity check on dates in time windows and geometry??

		dl := models.Download{}
		if err := c.Bind(&dl); err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}

		d, err := models.CreateDownload(db, dl)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}

		return c.JSON(http.StatusOK, d)
	}
}

// GetDownload gets a single download
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

/*
****************************
Example POST JSON BODY
****************************

{
	"id": "233bf9b3-9ca6-497f-806a-9d198a28abdb",
	"progress": 10
}
*/

//UpdateDownload updates the status, progress and datetime_end from the lambda function
func UpdateDownload(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {

		dl := models.Download{}
		if err := c.Bind(&dl); err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}

		d, err := models.UpdateDownload(db, dl)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}

		return c.JSON(http.StatusOK, d)

	}
}
