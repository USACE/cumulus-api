package models

import (
	"context"
	"strconv"
	"time"

	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v4/pgxpool"
)

// BasinCompsDailyResult represents a basin average result
type BasinCompsDailyResult struct {
	ID            uuid.UUID  `json:"id" db:"id"`
	RunDate       time.Time  `json:"run_date" db:"run_date"`
	DataDate      time.Time  `json:"data_date" db:"data_date"`
	DataDatetime  time.Time  `json:"data_datetime" db:"data_datetime"`
	BasinID       string     `json:"basin_id" db:"basin_id"`
	BasinName     string     `json:"basin_name" db:"basin_name"`
	ProductID     *uuid.UUID `json:"product_id" db:"product_id"`
	ProductName   *string    `json:"product_name" db:"product_name"`
	ProductSlug   string     `json:"product_slug" db:"product_slug"`
	IntervalHours int        `json:"interval_hours" db:"interval_hours"`
	Value         float64    `json:"value" db:"value"`
	Units         string     `json:"units" db:"units"`
	CreatedAt     time.Time  `json:"created_at" db:"created_at"`
}

// BasinCompsBatchRun represents a batch run
type BasinCompsBatchRun struct {
	ID           uuid.UUID    `json:"id" db:"id"`
	RunDate      time.Time    `json:"run_date" db:"run_date"`
	StartTime    time.Time    `json:"start_time" db:"start_time"`
	EndTime      *time.Time   `json:"end_time" db:"end_time"`
	Status       string       `json:"status" db:"status"`
	ProductIDs   []uuid.UUID  `json:"product_ids" db:"product_ids"`
	FileCount    *int         `json:"file_count" db:"file_count"`
	ResultCount  *int         `json:"result_count" db:"result_count"`
	CSVFileKey   *string      `json:"csv_file_key" db:"csv_file_key"`
	DSSFileKey   *string      `json:"dss_file_key" db:"dss_file_key"`
	ErrorMessage *string      `json:"error_message" db:"error_message"`
	CreatedAt    time.Time    `json:"created_at" db:"created_at"`
}

// GetBasinCompsResults retrieves results for date range and optional basin/product filter
func GetBasinCompsResults(
	db *pgxpool.Pool,
	startDate time.Time,
	endDate time.Time,
	basinID *string,
	productSlug *string,
	filter string,
) ([]BasinCompsDailyResult, error) {

	results := make([]BasinCompsDailyResult, 0)

	var query string
	var args []interface{}

	// Build query based on filter mode
	switch filter {
	case "latest_before":
		// Get most recent comp run BEFORE start_date
		query = `SELECT DISTINCT ON (basin_id, product_slug) * FROM v_basincomps_daily_result
		         WHERE run_date < $1`
		args = []interface{}{startDate}

	case "latest_after":
		// Get first comp run AT OR AFTER start_date
		query = `SELECT DISTINCT ON (basin_id, product_slug) * FROM v_basincomps_daily_result
		         WHERE run_date >= $1`
		args = []interface{}{startDate}

	case "latest_per_day":
		// Get most recent comp run for each calendar day in range
		// Uses DISTINCT ON to get latest run_date per day
		query = `SELECT DISTINCT ON (DATE(run_date AT TIME ZONE 'UTC'), basin_id, product_slug) *
		         FROM v_basincomps_daily_result
		         WHERE run_date >= $1 AND run_date < $2`
		args = []interface{}{startDate, endDate}

	case "all":
		fallthrough
	default:
		// Default: all comp runs in date range
		query = `SELECT * FROM v_basincomps_daily_result
		         WHERE run_date >= $1 AND run_date < $2`
		args = []interface{}{startDate, endDate}
	}

	// Add basin and product filters
	paramNum := len(args) + 1
	if basinID != nil {
		query += ` AND basin_id = $` + strconv.Itoa(paramNum)
		args = append(args, *basinID)
		paramNum++

		if productSlug != nil {
			query += ` AND product_slug = $` + strconv.Itoa(paramNum)
			args = append(args, *productSlug)
			paramNum++
		}
	} else if productSlug != nil {
		query += ` AND product_slug = $` + strconv.Itoa(paramNum)
		args = append(args, *productSlug)
		paramNum++
	}

	// Add ORDER BY and LIMIT based on filter mode
	switch filter {
	case "latest_before":
		// DISTINCT ON requires ORDER BY to start with same columns
		query += ` ORDER BY basin_id, product_slug, run_date DESC`
	case "latest_after":
		// DISTINCT ON requires ORDER BY to start with same columns
		query += ` ORDER BY basin_id, product_slug, run_date ASC`
	case "latest_per_day":
		// DISTINCT ON requires matching ORDER BY
		query += ` ORDER BY DATE(run_date AT TIME ZONE 'UTC'), basin_id, product_slug, run_date DESC`
	default:
		query += ` ORDER BY run_date DESC, data_datetime, basin_id`
	}

	err := pgxscan.Select(context.Background(), db, &results, query, args...)
	if err != nil {
		return nil, err
	}

	return results, nil
}

// ListBasinCompsBatchRuns retrieves recent batch runs
func ListBasinCompsBatchRuns(db *pgxpool.Pool, limit int) ([]BasinCompsBatchRun, error) {
	runs := make([]BasinCompsBatchRun, 0)

	err := pgxscan.Select(
		context.Background(), db, &runs,
		`SELECT * FROM basincomps_batch_run
         ORDER BY run_date DESC
         LIMIT $1`,
		limit,
	)
	if err != nil {
		return nil, err
	}

	return runs, nil
}

// BasinCompsShapefileConfig represents shapefile-specific configuration
type BasinCompsShapefileConfig struct {
	ID            uuid.UUID    `json:"id" db:"id"`
	ConfigName    string       `json:"config_name" db:"config_name"`
	Description   *string      `json:"description" db:"description"`
	ShapefilePath string       `json:"shapefile_path" db:"shapefile_path"`
	ProductIDs    []uuid.UUID  `json:"product_ids" db:"product_ids"`
	ProductNames  []string     `json:"product_names" db:"product_names"`
	ProductSlugs  []string     `json:"product_slugs" db:"product_slugs"`
	Enabled       bool         `json:"enabled" db:"enabled"`
	CreatedAt     time.Time    `json:"created_at" db:"created_at"`
	UpdatedAt     time.Time    `json:"updated_at" db:"updated_at"`
}

// BasinCompsRollingTotal represents rolling precipitation totals
type BasinCompsRollingTotal struct {
	ID           uuid.UUID  `json:"id" db:"id"`
	RunDate      time.Time  `json:"run_date" db:"run_date"`
	DataDate     time.Time  `json:"data_date" db:"data_date"`
	BasinID      string     `json:"basin_id" db:"basin_id"`
	BasinName    string     `json:"basin_name" db:"basin_name"`
	ProductID    *uuid.UUID `json:"product_id" db:"product_id"`
	ProductName  *string    `json:"product_name" db:"product_name"`
	ProductSlug  string     `json:"product_slug" db:"product_slug"`
	Days         int        `json:"days" db:"days"`
	TotalValue   float64    `json:"total_value" db:"total_value"`
	Units        string     `json:"units" db:"units"`
	CreatedAt    time.Time  `json:"created_at" db:"created_at"`
}

// ListShapefileConfigs retrieves all shapefile configurations
func ListShapefileConfigs(db *pgxpool.Pool) ([]BasinCompsShapefileConfig, error) {
	configs := make([]BasinCompsShapefileConfig, 0)

	err := pgxscan.Select(
		context.Background(), db, &configs,
		`SELECT * FROM v_basincomps_shapefile_config ORDER BY config_name`,
	)
	if err != nil {
		return nil, err
	}

	return configs, nil
}

// GetShapefileConfig retrieves a single shapefile configuration
func GetShapefileConfig(db *pgxpool.Pool, configName string) (*BasinCompsShapefileConfig, error) {
	var config BasinCompsShapefileConfig

	err := pgxscan.Get(
		context.Background(), db, &config,
		`SELECT * FROM v_basincomps_shapefile_config WHERE config_name = $1`,
		configName,
	)
	if err != nil {
		return nil, err
	}

	return &config, nil
}

// CreateShapefileConfig creates a new shapefile configuration
func CreateShapefileConfig(db *pgxpool.Pool, configName string, description *string, shapefilePath string, productIDs []uuid.UUID) (*BasinCompsShapefileConfig, error) {
	_, err := db.Exec(
		context.Background(),
		`INSERT INTO basincomps_shapefile_config (config_name, description, shapefile_path, product_ids)
         VALUES ($1, $2, $3, $4)
         ON CONFLICT (config_name) DO UPDATE
         SET description = EXCLUDED.description,
             shapefile_path = EXCLUDED.shapefile_path,
             product_ids = EXCLUDED.product_ids,
             updated_at = NOW()`,
		configName, description, shapefilePath, productIDs,
	)
	if err != nil {
		return nil, err
	}

	return GetShapefileConfig(db, configName)
}

// UpdateShapefileConfig updates an existing shapefile configuration
func UpdateShapefileConfig(db *pgxpool.Pool, configName string, description *string, shapefilePath string, productIDs []uuid.UUID, enabled bool) (*BasinCompsShapefileConfig, error) {
	_, err := db.Exec(
		context.Background(),
		`UPDATE basincomps_shapefile_config
         SET description = $2, shapefile_path = $3, product_ids = $4, enabled = $5, updated_at = NOW()
         WHERE config_name = $1`,
		configName, description, shapefilePath, productIDs, enabled,
	)
	if err != nil {
		return nil, err
	}

	return GetShapefileConfig(db, configName)
}

// GetRollingTotals retrieves rolling totals for date range
func GetRollingTotals(
	db *pgxpool.Pool,
	startDate time.Time,
	endDate time.Time,
	basinID *string,
	productSlug *string,
	days *int,
	filter string,
) ([]BasinCompsRollingTotal, error) {

	totals := make([]BasinCompsRollingTotal, 0)

	var query string
	var args []interface{}

	// Build query based on filter mode (same as GetBasinCompsResults)
	switch filter {
	case "latest_before":
		query = `SELECT DISTINCT ON (basin_id, product_slug) * FROM v_basincomps_rolling_total
		         WHERE run_date < $1`
		args = []interface{}{startDate}

	case "latest_after":
		query = `SELECT DISTINCT ON (basin_id, product_slug) * FROM v_basincomps_rolling_total
		         WHERE run_date >= $1`
		args = []interface{}{startDate}

	case "latest_per_day":
		query = `SELECT DISTINCT ON (DATE(run_date AT TIME ZONE 'UTC'), basin_id, product_slug, days) *
		         FROM v_basincomps_rolling_total
		         WHERE run_date >= $1 AND run_date < $2`
		args = []interface{}{startDate, endDate}

	case "all":
		fallthrough
	default:
		query = `SELECT * FROM v_basincomps_rolling_total
		         WHERE run_date >= $1 AND run_date < $2`
		args = []interface{}{startDate, endDate}
	}

	// Add basin, product, and days filters with dynamic parameter numbering
	paramNum := len(args) + 1
	if basinID != nil {
		query += ` AND basin_id = $` + strconv.Itoa(paramNum)
		args = append(args, *basinID)
		paramNum++

		if productSlug != nil {
			query += ` AND product_slug = $` + strconv.Itoa(paramNum)
			args = append(args, *productSlug)
			paramNum++

			if days != nil {
				query += ` AND days = $` + strconv.Itoa(paramNum)
				args = append(args, *days)
				paramNum++
			}
		} else if days != nil {
			query += ` AND days = $` + strconv.Itoa(paramNum)
			args = append(args, *days)
			paramNum++
		}
	} else if productSlug != nil {
		query += ` AND product_slug = $` + strconv.Itoa(paramNum)
		args = append(args, *productSlug)
		paramNum++

		if days != nil {
			query += ` AND days = $` + strconv.Itoa(paramNum)
			args = append(args, *days)
			paramNum++
		}
	} else if days != nil {
		query += ` AND days = $` + strconv.Itoa(paramNum)
		args = append(args, *days)
		paramNum++
	}

	// Add ORDER BY and LIMIT based on filter mode
	switch filter {
	case "latest_before":
		// DISTINCT ON requires ORDER BY to start with same columns
		query += ` ORDER BY basin_id, product_slug, run_date DESC, days`
	case "latest_after":
		// DISTINCT ON requires ORDER BY to start with same columns
		query += ` ORDER BY basin_id, product_slug, run_date ASC, days`
	case "latest_per_day":
		// DISTINCT ON requires matching ORDER BY
		query += ` ORDER BY DATE(run_date AT TIME ZONE 'UTC'), basin_id, product_slug, days, run_date DESC`
	default:
		query += ` ORDER BY run_date DESC, data_date DESC, basin_id, days`
	}

	err := pgxscan.Select(context.Background(), db, &totals, query, args...)
	if err != nil {
		return nil, err
	}

	return totals, nil
}
