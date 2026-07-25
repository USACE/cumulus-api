package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/USACE/cumulus-api/api/config"
	"github.com/USACE/cumulus-api/api/messages"
	"github.com/USACE/cumulus-api/api/models"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"
)

// import (
// 	"api/models"
// 	"net/http"

// 	"github.com/google/uuid"
// 	"github.com/jmoiron/sqlx"
// 	"github.com/labstack/echo/v4"
// )

// /*
// ****************************
// Example POST JSON BODY
// ****************************
// {
// 	"datetime_start": "2020-08-15T00:00:00Z",
// 	"datetime_end": "2020-08-17T00:00:00Z",
// 	"product_id": [
// 		"e0baa220-1310-445b-816b-6887465cc94b",
// 		"757c809c-dda0-412b-9831-cb9bd0f62d1d"
// 	]
// }
// */

// ListDownloads returns an array of all downloads
func ListDownloads(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		dd, err := models.ListDownloads(db)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, dd)
	}
}

// ListAdminDownloads returns downloads for admin
func ListAdminDownloads(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		dd, err := models.ListAdminDownloads(db)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, dd)
	}
}

// parseUsageQueryParams parses the after/before/limit query params shared by
// the admin usage-report endpoints. limit defaults to 10 and is capped at 200.
func parseUsageQueryParams(c echo.Context) (after, before *time.Time, limit int, err error) {
	limit = 10
	if v := c.QueryParam("after"); v != "" {
		t, e := time.Parse(time.RFC3339, v)
		if e != nil {
			return nil, nil, 0, fmt.Errorf("invalid after format")
		}
		after = &t
	}
	if v := c.QueryParam("before"); v != "" {
		t, e := time.Parse(time.RFC3339, v)
		if e != nil {
			return nil, nil, 0, fmt.Errorf("invalid before format")
		}
		before = &t
	}
	if v := c.QueryParam("limit"); v != "" {
		l, e := strconv.Atoi(v)
		if e != nil || l <= 0 {
			return nil, nil, 0, fmt.Errorf("invalid limit")
		}
		if l > 200 {
			l = 200
		}
		limit = l
	}
	return after, before, limit, nil
}

// ListDownloadUsage returns per-user download usage stats for admins, sortable
// and filterable via query params: sort (downloaded|packaged|requests|retrievals,
// default downloaded), order (asc|desc), q (name/email/sub substring),
// after/before (RFC3339), limit.
func ListDownloadUsage(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		after, before, limit, err := parseUsageQueryParams(c)
		if err != nil {
			return c.JSON(http.StatusBadRequest, messages.NewMessage(err.Error()))
		}
		f := models.DownloadUsageFilter{
			Sort:   c.QueryParam("sort"),
			Order:  c.QueryParam("order"),
			Q:      c.QueryParam("q"),
			After:  after,
			Before: before,
			Limit:  limit,
		}

		uu, err := models.ListDownloadUsage(db, f)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, uu)
	}
}

// ListProductUsage returns the most-downloaded products, user-agnostic
// (aggregated across everyone). Sortable only by request count -- see
// models.ProductUsageFilter for why a GB metric isn't offered here.
// Query params: order (asc|desc), q (product name/slug substring),
// after/before (RFC3339), limit.
func ListProductUsage(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		after, before, limit, err := parseUsageQueryParams(c)
		if err != nil {
			return c.JSON(http.StatusBadRequest, messages.NewMessage(err.Error()))
		}
		f := models.ProductUsageFilter{
			Order:  c.QueryParam("order"),
			Q:      c.QueryParam("q"),
			After:  after,
			Before: before,
			Limit:  limit,
		}

		pp, err := models.ListProductUsage(db, f)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, pp)
	}
}

// parseUsageFilter parses the multi-value filter shared by the analytics
// endpoints: repeatable user/product (UUID) and extent (string) params plus
// after/before (RFC3339). Repeat a param to select several values, e.g.
// ?user=<a>&user=<b>&product=<c>.
func parseUsageFilter(c echo.Context) (models.UsageFilter, error) {
	var f models.UsageFilter

	for _, s := range c.QueryParams()["user"] {
		if s == "" {
			continue
		}
		id, err := uuid.Parse(s)
		if err != nil {
			return f, fmt.Errorf("invalid user id")
		}
		f.Users = append(f.Users, id)
	}
	for _, s := range c.QueryParams()["product"] {
		if s == "" {
			continue
		}
		id, err := uuid.Parse(s)
		if err != nil {
			return f, fmt.Errorf("invalid product id")
		}
		f.Products = append(f.Products, id)
	}
	for _, s := range c.QueryParams()["extent"] {
		if s != "" {
			f.Extents = append(f.Extents, s)
		}
	}
	if v := c.QueryParam("after"); v != "" {
		t, err := time.Parse(time.RFC3339, v)
		if err != nil {
			return f, fmt.Errorf("invalid after format")
		}
		f.After = &t
	}
	if v := c.QueryParam("before"); v != "" {
		t, err := time.Parse(time.RFC3339, v)
		if err != nil {
			return f, fmt.Errorf("invalid before format")
		}
		f.Before = &t
	}
	// Breakdown cap: default top-N; an explicit limit<=0 means uncapped (the
	// CSV export passes limit=0 to get every row). Only GetUsageSummary reads
	// this; the timeseries handler ignores it.
	f.Limit = models.DefaultSummaryLimit
	if v := c.QueryParam("limit"); v != "" {
		n, err := strconv.Atoi(v)
		if err != nil {
			return f, fmt.Errorf("invalid limit")
		}
		f.Limit = n
	}
	return f, nil
}

// GetUsageSummary returns totals plus per-user, per-product and per-extent
// breakdowns for the filtered download set. Query params: repeatable
// user/product/extent, after/before (RFC3339), and limit (top-N per breakdown;
// limit<=0 returns every row -- used by the CSV export).
func GetUsageSummary(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		f, err := parseUsageFilter(c)
		if err != nil {
			return c.JSON(http.StatusBadRequest, messages.NewMessage(err.Error()))
		}
		summary, err := models.GetUsageSummary(db, f)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, summary)
	}
}

// GetUsageTimeseries returns request volume over time for the filtered set.
// Query params: repeatable user/product/extent, after/before (RFC3339),
// interval (day|week|month, default day).
func GetUsageTimeseries(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		f, err := parseUsageFilter(c)
		if err != nil {
			return c.JSON(http.StatusBadRequest, messages.NewMessage(err.Error()))
		}
		// Validate interval here so a bad value is a clean 400 and any error the
		// model returns can be treated as a server/DB error (500) without
		// leaking internal error text to the client.
		interval := c.QueryParam("interval")
		switch interval {
		case "", "day", "week", "month":
		default:
			return c.JSON(http.StatusBadRequest, messages.NewMessage("invalid interval (day|week|month)"))
		}
		pts, err := models.GetUsageTimeseries(db, f, interval)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, pts)
	}
}

// ListUsageUsers returns the distinct downloading users for the analytics
// user selector.
func ListUsageUsers(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		uu, err := models.ListUsageUsers(db)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, uu)
	}
}

// ListMyDownloads returns an array of downloads for a sub
func ListMyDownloads(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		sub, err := GetSub(c)
		if err != nil {
			return c.JSON(http.StatusBadRequest, models.DefaultMessageBadRequest)
		}
		dd, err := models.ListMyDownloads(db, sub)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, dd)
	}
}

// CreateDownload creates record of a new download
func CreateDownload(db *pgxpool.Pool, cfg *config.Config) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Parse the raw request to handle GeoJSON
		var rawRequest map[string]interface{}
		if err := c.Bind(&rawRequest); err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}

		// Build the download request
		var dr models.DownloadRequest

		// Parse datetime fields
		if dtStart, ok := rawRequest["datetime_start"].(string); ok {
			if t, err := time.Parse(time.RFC3339, dtStart); err == nil {
				dr.DatetimeStart = t
			} else {
				return c.JSON(http.StatusBadRequest, messages.NewMessage("Invalid datetime_start format"))
			}
		}

		if dtEnd, ok := rawRequest["datetime_end"].(string); ok {
			if t, err := time.Parse(time.RFC3339, dtEnd); err == nil {
				dr.DatetimeEnd = t
			} else {
				return c.JSON(http.StatusBadRequest, messages.NewMessage("Invalid datetime_end format"))
			}
		}

		// Parse watershed_id if provided
		if wid, ok := rawRequest["watershed_id"].(string); ok {
			if id, err := uuid.Parse(wid); err == nil {
				dr.WatershedID = &id
			}
		}

		// Parse user_region_id if provided - load the region's GeoJSON
		if regionID, ok := rawRequest["user_region_id"].(string); ok {
			if rid, err := uuid.Parse(regionID); err == nil {
				// Get the user's sub
				sub, err := GetSub(c)
				if err != nil {
					return c.JSON(http.StatusUnauthorized, models.DefaultMessageUnauthorized)
				}

				// Fetch the user region
				region, err := models.GetUserRegion(db, &rid, sub)
				if err != nil {
					return c.JSON(http.StatusBadRequest, messages.NewMessage("User region not found or not accessible"))
				}

				// Use the region's GeoJSON and name
				geojsonStr := string(region.GeoJSON)
				dr.ClipGeoJSON = &geojsonStr
				dr.ClipRegionName = &region.Name
			}
		}

		// Parse product_id array
		if products, ok := rawRequest["product_id"].([]interface{}); ok {
			dr.ProductID = make([]uuid.UUID, 0)
			for _, p := range products {
				if pid, ok := p.(string); ok {
					if id, err := uuid.Parse(pid); err == nil {
						dr.ProductID = append(dr.ProductID, id)
					}
				}
			}
		}

		// Parse format
		if format, ok := rawRequest["format"].(string); ok {
			dr.Format = &format
		}

		// Parse clip_region_name (if not set from user_region)
		if dr.ClipRegionName == nil {
			if name, ok := rawRequest["clip_region_name"].(string); ok {
				dr.ClipRegionName = &name
			}
		}

		// Parse and convert clip_geojson to string (if not set from user_region)
		if dr.ClipGeoJSON == nil {
			if geojson, ok := rawRequest["clip_geojson"]; ok && geojson != nil {
				geojsonBytes, err := json.Marshal(geojson)
				if err != nil {
					return c.JSON(http.StatusBadRequest, messages.NewMessage("Invalid GeoJSON format"))
				}
				geojsonStr := string(geojsonBytes)
				dr.ClipGeoJSON = &geojsonStr
			}
		}

		// Validate that either watershed_id, clip_geojson, or user_region_id was provided
		if dr.WatershedID == nil && dr.ClipGeoJSON == nil {
			return c.JSON(
				http.StatusBadRequest,
				messages.NewMessage("Either watershed_id, user_region_id, or clip_geojson must be provided"),
			)
		}

		// If both are provided, prefer custom clip region
		if dr.WatershedID != nil && dr.ClipGeoJSON != nil {
			// Log or handle as needed - using custom region over watershed
			dr.WatershedID = nil // Clear watershed ID to use custom region
		}

		// If output format unspecified, use default format
		if dr.Format == nil {
			dr.Format = &cfg.DownloadDefaultFormat
		}
		// Set subject
		sub, err := GetSub(c)
		if err != nil {
			return c.JSON(http.StatusUnauthorized, models.DefaultMessageUnauthorized)
		}
		dr.Sub = sub

		// limit to 183 days, just over 6 months (4392 hours) window, return client error if exceeded
		diff := dr.DatetimeEnd.Sub(dr.DatetimeStart)
		if diff.Hours() > 4392 {
			return c.JSON(
				http.StatusBadRequest,
				messages.NewMessage("Time window too large.  Must be less than 6 months"),
			)
		}

		d, err := models.CreateDownload(db, &dr)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}

		return c.JSON(http.StatusCreated, d)
	}
}

// GetDownload gets a single download
func GetDownload(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		downloadID, err := uuid.Parse(c.Param("download_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		dl, err := models.GetDownload(db, &downloadID)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, dl)
	}
}

// /*
// ****************************
// Example PUT JSON BODY
// ****************************
// {
// 	"id": "233bf9b3-9ca6-497f-806a-9d198a28abdb",
// 	"progress": 100,
// 	"status_id": "3914f0bd-2290-42b1-bc24-41479b3a846f"
// }
// */

// GetDownloadPackagerRequest is an endpoint used by packager to get information about records
// that must go into the download package
func GetDownloadPackagerRequest(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		downloadID, err := uuid.Parse(c.Param("download_id"))
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		// Request context so a packager that gives up (or a proxy that 504s) cancels the query
		// instead of leaving it running against the connection pool.
		dpr, err := models.GetDownloadPackagerRequest(c.Request().Context(), db, &downloadID)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSON(http.StatusOK, dpr)
	}
}

// UpdateDownload updates the status, progress and datetime_end from the lambda function
func UpdateDownload(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		var u models.PackagerInfo
		if err := c.Bind(&u); err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		// Set Download ID from Route Params
		downloadID, err := uuid.Parse(c.Param("download_id"))
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

// GetDownloadMetrics returns metrics
func GetDownloadMetrics(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		dm, err := models.GetDownloadMetrics(db)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}
		return c.JSONBlob(http.StatusOK, dm)
	}
}
