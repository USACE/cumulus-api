package handlers

import (
	"net/http"
	"strconv"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"

	"github.com/USACE/cumulus-api/api/models"
)

// ServeDownloadFile streams a completed download's package to the client.
// Unlike a bearer-JWT-gated route, this must work with a plain browser
// navigation (the frontend calls window.open on the link), so access is
// controlled by a short-lived HMAC signature (exp/sig query params) rather
// than an Authorization header. The S3 key is always resolved server-side
// from the download row -- never taken from client input -- and each
// successful fetch increments that download's retrieval_count.
func ServeDownloadFile(db *pgxpool.Pool, awsCfg *aws.Config, bucket *string, forcePathStyle bool, linkSecret string) echo.HandlerFunc {
	return func(c echo.Context) error {
		downloadID, err := uuid.Parse(c.Param("download_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "invalid download id")
		}

		exp, err := strconv.ParseInt(c.QueryParam("exp"), 10, 64)
		if err != nil || !models.ValidDownloadLink(linkSecret, downloadID, exp, c.QueryParam("sig")) {
			return c.String(http.StatusForbidden, "link expired or invalid")
		}

		d, err := models.GetDownload(db, &downloadID)
		if err != nil || d.RawFile == nil {
			return c.String(http.StatusNotFound, "not found")
		}

		client := s3.NewFromConfig(*awsCfg, func(o *s3.Options) {
			o.UsePathStyle = forcePathStyle
		})
		output, err := client.GetObject(c.Request().Context(), &s3.GetObjectInput{Bucket: bucket, Key: aws.String(*d.RawFile)})
		if err != nil {
			return c.String(http.StatusNotFound, "not found")
		}

		if err := models.IncrementDownloadRetrieval(db, &downloadID); err != nil {
			c.Logger().Errorf("failed to record download retrieval for %s: %v", downloadID, err)
		}

		c.Response().Header().Set(echo.HeaderContentDisposition, "attachment")
		return c.Stream(http.StatusOK, "application/octet-stream", output.Body)
	}
}
