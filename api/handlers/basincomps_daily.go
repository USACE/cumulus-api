package handlers

import (
	"context"
	"net/http"
	"strconv"
	"time"

	"github.com/USACE/cumulus-api/api/models"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v4/pgxpool"
	"github.com/labstack/echo/v4"
)

// GetBasinCompsResults retrieves basin average results
func GetBasinCompsResults(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Parse query parameters
		startDateStr := c.QueryParam("start_date")
		endDateStr := c.QueryParam("end_date")
		basinID := c.QueryParam("basin_id")
		productSlug := c.QueryParam("product_slug")
		filter := c.QueryParam("filter") // all (default), latest_before, latest_after, latest_per_day

		// Default to last 7 days if not specified
		endDate := time.Now()
		startDate := endDate.AddDate(0, 0, -7)

		if startDateStr != "" {
			// Try RFC3339 format first (with timezone): "2006-01-02T15:04:05Z07:00"
			if parsed, err := time.Parse(time.RFC3339, startDateStr); err == nil {
				startDate = parsed
			} else if parsed, err := time.Parse("2006-01-02", startDateStr); err == nil {
				// Fallback to date-only format for backward compatibility (assumes UTC)
				startDate = parsed
			}
		}

		if endDateStr != "" {
			// Try RFC3339 format first (with timezone): "2006-01-02T15:04:05Z07:00"
			if parsed, err := time.Parse(time.RFC3339, endDateStr); err == nil {
				endDate = parsed
			} else if parsed, err := time.Parse("2006-01-02", endDateStr); err == nil {
				// Fallback to date-only format for backward compatibility (assumes UTC)
				// Add 1 day to make the date range inclusive (since query uses run_date < endDate)
				endDate = parsed.AddDate(0, 0, 1)
			}
		}

		var basinIDPtr *string
		if basinID != "" {
			basinIDPtr = &basinID
		}

		var productSlugPtr *string
		if productSlug != "" {
			productSlugPtr = &productSlug
		}

		// Default filter to "all" if not specified
		if filter == "" {
			filter = "all"
		}

		results, err := models.GetBasinCompsResults(
			db, startDate, endDate, basinIDPtr, productSlugPtr, filter,
		)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}

		return c.JSON(http.StatusOK, results)
	}
}

// ListBasinCompsBatchRuns lists recent batch runs
func ListBasinCompsBatchRuns(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		runs, err := models.ListBasinCompsBatchRuns(db, 30)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}

		return c.JSON(http.StatusOK, runs)
	}
}

// ListShapefileConfigs retrieves all shapefile configurations
func ListShapefileConfigs(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		configs, err := models.ListShapefileConfigs(db)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}

		return c.JSON(http.StatusOK, configs)
	}
}

// GetShapefileConfig retrieves a single shapefile configuration
func GetShapefileConfig(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		configName := c.Param("config_name")

		config, err := models.GetShapefileConfig(db, configName)
		if err != nil {
			return c.String(http.StatusNotFound, err.Error())
		}

		return c.JSON(http.StatusOK, config)
	}
}

// CreateOrUpdateShapefileConfig creates or updates a shapefile configuration
func CreateOrUpdateShapefileConfig(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		configName := c.Param("config_name")

		var req struct {
			Description   *string  `json:"description"`
			ShapefilePath string   `json:"shapefile_path"`
			ProductIDs    []string `json:"product_ids"`
			Enabled       *bool    `json:"enabled"`
		}

		if err := c.Bind(&req); err != nil {
			return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid request"})
		}

		// Validate required fields
		if req.ShapefilePath == "" {
			return c.JSON(http.StatusBadRequest, map[string]string{"error": "shapefile_path is required"})
		}

		// Parse product IDs
		productIDs := make([]uuid.UUID, 0)
		for _, pidStr := range req.ProductIDs {
			pid, err := uuid.Parse(pidStr)
			if err != nil {
				return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid product_id format"})
			}
			productIDs = append(productIDs, pid)
		}

		// Check if config exists
		existing, err := models.GetShapefileConfig(db, configName)

		var config *models.BasinCompsShapefileConfig
		if err != nil {
			// Create new
			config, err = models.CreateShapefileConfig(db, configName, req.Description, req.ShapefilePath, productIDs)
		} else {
			// Update existing
			enabled := true
			if req.Enabled != nil {
				enabled = *req.Enabled
			} else {
				enabled = existing.Enabled
			}
			config, err = models.UpdateShapefileConfig(db, configName, req.Description, req.ShapefilePath, productIDs, enabled)
		}

		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}

		return c.JSON(http.StatusOK, config)
	}
}

// GetRollingTotals retrieves rolling precipitation totals
func GetRollingTotals(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Parse query parameters
		startDateStr := c.QueryParam("start_date")
		endDateStr := c.QueryParam("end_date")
		basinID := c.QueryParam("basin_id")
		productSlug := c.QueryParam("product_slug")
		daysStr := c.QueryParam("days")
		filter := c.QueryParam("filter") // all (default), latest_before, latest_after, latest_per_day

		// Default to last 7 days
		endDate := time.Now()
		startDate := endDate.AddDate(0, 0, -7)

		if startDateStr != "" {
			// Try RFC3339 format first (with timezone): "2006-01-02T15:04:05Z07:00"
			if parsed, err := time.Parse(time.RFC3339, startDateStr); err == nil {
				startDate = parsed
			} else if parsed, err := time.Parse("2006-01-02", startDateStr); err == nil {
				// Fallback to date-only format for backward compatibility (assumes UTC)
				startDate = parsed
			}
		}

		if endDateStr != "" {
			// Try RFC3339 format first (with timezone): "2006-01-02T15:04:05Z07:00"
			if parsed, err := time.Parse(time.RFC3339, endDateStr); err == nil {
				endDate = parsed
			} else if parsed, err := time.Parse("2006-01-02", endDateStr); err == nil {
				// Fallback to date-only format for backward compatibility (assumes UTC)
				// Add 1 day to make the date range inclusive (since query uses run_date < endDate)
				endDate = parsed.AddDate(0, 0, 1)
			}
		}

		var basinIDPtr *string
		if basinID != "" {
			basinIDPtr = &basinID
		}

		var productSlugPtr *string
		if productSlug != "" {
			productSlugPtr = &productSlug
		}

		var daysPtr *int
		if daysStr != "" {
			if days, err := strconv.Atoi(daysStr); err == nil && days >= 1 && days <= 7 {
				daysPtr = &days
			}
		}

		// Default filter to "all" if not specified
		if filter == "" {
			filter = "all"
		}

		totals, err := models.GetRollingTotals(
			db, startDate, endDate, basinIDPtr, productSlugPtr, daysPtr, filter,
		)
		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}

		return c.JSON(http.StatusOK, totals)
	}
}

// TriggerBasinCompsRun manually triggers a BasinComps batch run
func TriggerBasinCompsRun(db *pgxpool.Pool) echo.HandlerFunc {
	return func(c echo.Context) error {
		// Call stored procedure to trigger batch run
		// This uses SECURITY DEFINER to prevent direct table access
		var batchID *string
		var message string

		err := db.QueryRow(
			context.Background(),
			`SELECT batch_id::text, message FROM cumulus.trigger_basincomps_run()`,
		).Scan(&batchID, &message)

		if err != nil {
			return c.String(http.StatusInternalServerError, err.Error())
		}

		return c.JSON(http.StatusAccepted, map[string]string{
			"message":  message,
			"batch_id": func() string { if batchID != nil { return *batchID } else { return "" } }(),
		})
	}
}
