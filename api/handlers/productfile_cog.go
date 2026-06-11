package handlers

import (
	"fmt"
	"log"
	"net/http"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"

	"github.com/USACE/cumulus-api/api/middleware"
	"github.com/USACE/cumulus-api/api/models"

	_ "github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

// ListProductfilesCOG returns the productfiles for a product over a time range as
// directly-readable COG proxy URLs (each backed by StreamProductfileCOG, which is
// Range-capable so a GDAL /vsicurl/ client can read tiles). Same query params as
// ListProductfiles: 'after' and 'before' (RFC3339).
func ListProductfilesCOG(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		id, err := uuid.Parse(c.Param("product_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "Malformed ID")
		}
		after := c.QueryParam("after")
		before := c.QueryParam("before")
		if after == "" || before == "" {
			return c.String(
				http.StatusBadRequest,
				"Missing query parameter 'after' or 'before'",
			)
		}

		ff, err := models.ListProductfiles(db, id, after, before)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}

		cogs := make([]models.ProductfileCOG, 0, len(ff))
		for _, f := range ff {
			cogs = append(cogs, models.ProductfileCOG{
				ID:       f.ID,
				Datetime: f.Datetime,
				Version:  f.Version,
				CogURL:   fmt.Sprintf("/api/products/%s/cog/%s", id.String(), f.ID.String()),
			})
		}
		return c.JSON(http.StatusOK, cogs)
	}
}

// StreamProductfileCOG streams a productfile's COG object from S3, passing the
// inbound HTTP Range header through to S3 and returning 206 Partial Content with
// Content-Range/Accept-Ranges so a GDAL /vsicurl/ client can read tiles directly
// (no full download). HEAD returns size + range support for /vsicurl/ probing.
// Every request is authenticated (private route) and logged for metering.
func StreamProductfileCOG(db *pgxpool.Pool, awsCfg *aws.Config, forcePathStyle bool) echo.HandlerFunc {
	return func(c echo.Context) error {
		pfID, err := uuid.Parse(c.Param("productfile_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, "Malformed productfile ID")
		}

		obj, err := models.GetProductfileObject(db, pfID)
		if err != nil {
			return c.String(http.StatusNotFound, "Productfile not found")
		}

		ctx := c.Request().Context()
		// Endpoint/scheme come from the environment (AWS_ENDPOINT_URL_S3) via
		// awsCfg; only path-style addressing still needs to be set per-client.
		client := s3.NewFromConfig(*awsCfg, func(o *s3.Options) {
			o.UsePathStyle = forcePathStyle
		})

		// HEAD: metadata only (size + range support) for /vsicurl/ probing.
		if c.Request().Method == http.MethodHead {
			head, err := client.HeadObject(ctx, &s3.HeadObjectInput{Bucket: &obj.Bucket, Key: &obj.Key})
			if err != nil {
				return c.String(http.StatusInternalServerError, err.Error())
			}
			h := c.Response().Header()
			h.Set("Accept-Ranges", "bytes")
			if head.ContentLength != nil {
				h.Set(echo.HeaderContentLength, fmt.Sprintf("%d", *head.ContentLength))
			}
			c.Response().WriteHeader(http.StatusOK)
			return nil
		}

		in := &s3.GetObjectInput{Bucket: &obj.Bucket, Key: &obj.Key}
		if rangeHeader := c.Request().Header.Get("Range"); rangeHeader != "" {
			in.Range = aws.String(rangeHeader)
		}

		out, err := client.GetObject(ctx, in)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		defer out.Body.Close()

		h := c.Response().Header()
		h.Set("Accept-Ranges", "bytes")
		status := http.StatusOK
		if out.ContentRange != nil {
			h.Set("Content-Range", *out.ContentRange)
			status = http.StatusPartialContent
		}
		if out.ContentLength != nil {
			h.Set(echo.HeaderContentLength, fmt.Sprintf("%d", *out.ContentLength))
		}

		// Metering hook: who pulled which productfile and how many bytes. This is the
		// natural place to enforce a future per-user rate limit / quota.
		var bytesServed int64
		if out.ContentLength != nil {
			bytesServed = *out.ContentLength
		}
		logCOGAccess(c, pfID, bytesServed)

		return c.Stream(status, "application/octet-stream", out.Body)
	}
}

func logCOGAccess(c echo.Context, productfileID uuid.UUID, bytes int64) {
	sub := "key-auth"
	if ui, ok := c.Get("userInfo").(middleware.UserInfo); ok && ui.Sub != nil {
		sub = ui.Sub.String()
	}
	log.Printf("cog-access sub=%s productfile=%s bytes=%d", sub, productfileID.String(), bytes)
}
