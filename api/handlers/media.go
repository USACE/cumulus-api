package handlers

import (
	"fmt"
	"net/http"
	"path"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"

	"github.com/USACE/cumulus-api/api/models"
)

// ServeDownloadFile streams a completed download's package to the client.
//
// This must work with a plain browser navigation (the frontend calls
// window.open on the link) and with HEC-RTS, which fetches the link with no
// credentials, so the route carries no auth. What bounds access instead is the
// package's age: a download stops being fetchable downloadLinkLifetime after the
// packager finished with it, and there is no way to extend that -- the deadline
// comes from the download row, so re-requesting the link yields the same one.
// Users re-run the packager to get a fresh package.
//
// The S3 key is always resolved server-side from the download row, never from
// client input: the :filename path segment exists only so browsers and RTS
// derive a sensible local filename, and is not read here. Each successful fetch
// increments that download's retrieval_count.
func ServeDownloadFile(db *pgxpool.Pool, s3Client *s3.Client, bucket *string) echo.HandlerFunc {
	return func(c echo.Context) error {
		downloadID, err := uuid.Parse(c.Param("download_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "invalid download id")
		}

		d, err := models.GetDownload(db, &downloadID)
		if err != nil || d.RawFile == nil {
			return c.String(http.StatusNotFound, "not found")
		}
		if d.FileLinkExpired() {
			return c.String(http.StatusGone, "this download has expired; request the package again")
		}

		output, err := s3Client.GetObject(c.Request().Context(), &s3.GetObjectInput{Bucket: bucket, Key: aws.String(*d.RawFile)})
		if err != nil {
			return c.String(http.StatusNotFound, "not found")
		}

		if err := models.IncrementDownloadRetrieval(db, &downloadID); err != nil {
			c.Logger().Errorf("failed to record download retrieval for %s: %v", downloadID, err)
		}

		// Name the attachment explicitly. Browsers otherwise fall back to the last
		// path segment, which is how a link ending in "/file" produced a download
		// literally named "file".
		c.Response().Header().Set(
			echo.HeaderContentDisposition,
			fmt.Sprintf("attachment; filename=%q", path.Base(*d.RawFile)),
		)
		return c.Stream(http.StatusOK, "application/octet-stream", output.Body)
	}
}
