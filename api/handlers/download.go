package handlers

import (
	"api/models"
	"net/http"

	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	"github.com/labstack/echo/v4"
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

// ListMyDownloads returns an array of downloads for a ProfileID
func ListMyDownloads(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		p, err := profileFromContext(c, db)
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		dd, err := models.ListMyDownloads(db, &p.ID)
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
		var dr models.DownloadRequest
		if err := c.Bind(&dr); err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		// TODO: Cleanup and support CAC or Token to get Profile
		p, err := profileFromContext(c, db)
		// ProfileID is null (allows anon downloads)
		if err != nil || p == nil {
			dr.ProfileID = nil
		} else {
			// Attach ProfileID to Download Request if authenticated request
			dr.ProfileID = &p.ID
		}
		d, err := models.CreateDownload(db, &dr)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}

		return c.JSON(http.StatusCreated, d)
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
Example PUT JSON BODY
****************************
{
	"id": "233bf9b3-9ca6-497f-806a-9d198a28abdb",
	"progress": 100,
	"status_id": "3914f0bd-2290-42b1-bc24-41479b3a846f"
}
*/

// GetDownloadPackagerRequest is an endpoint used by packager to get information about records
// that must go into the download package
func GetDownloadPackagerRequest(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		downloadID, err := uuid.Parse(c.Param("id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		dpr, err := models.GetDownloadPackagerRequest(db, &downloadID)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, dpr)
	}
}

//UpdateDownload updates the status, progress and datetime_end from the lambda function
func UpdateDownload(db *sqlx.DB) echo.HandlerFunc {
	return func(c echo.Context) error {

		var u models.PackagerInfo
		if err := c.Bind(&u); err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		// Set Download ID from Route Params
		downloadID, err := uuid.Parse(c.Param("id"))
		if err != nil {
			return c.JSON(http.StatusBadRequest, err)
		}

		d, err := models.UpdateDownload(db, &downloadID, &u)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}

		return c.JSON(http.StatusOK, d)

	}
}
