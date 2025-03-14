package models

import (
	"context"

	// Postgres Database Driver
	"github.com/georgysavva/scany/pgxscan"
	"github.com/google/uuid"
	_ "github.com/jackc/pgx/v4"
	"github.com/jackc/pgx/v4/pgxpool"
)

// ProductSeriesInfo holds information required to create a product series
type ProductSeriesInfo struct {
	Name               string     `json:"name"`
	TemporalResolution *int       `json:"temporal_resolution" db:"temporal_resolution"`
	TemporalDuration   *int       `json:"temporal_duration" db:"temporal_duration"`
	DssFpart           string     `json:"dss_fpart" db:"dss_fpart"`
	DssDatatypeID      *uuid.UUID `json:"dss_datatype_id,omitempty" db:"dss_datatype_id"`
	DssDatatype        string     `json:"dss_datatype" db:"dss_datatype"`
	ParameterID        uuid.UUID  `json:"parameter_id" db:"parameter_id"`
	Parameter          string     `json:"parameter"`
	UnitID             uuid.UUID  `json:"unit_id" db:"unit_id"`
	Unit               string     `json:"unit"`
	Description        string     `json:"description"`
	SuiteID            uuid.UUID  `json:"suite_id" db:"suite_id"`
	Suite              string     `json:"suite"`
	Label              string     `json:"label"`
}

type ProductSeries struct {
	ProductIdentifiers
	Tags []uuid.UUID `json:"tags" db:"tags"`
	ProductSeriesInfo
	CoverageSummary
}

var listProductSeriesSQL = `SELECT id, slug, name, label, tags, temporal_resolution, temporal_duration,
								parameter_id, parameter, unit_id, unit, dss_fpart, dss_datatype_id, 
								dss_datatype, description, suite_id, suite, after, before, 
								productfile_count, last_forecast_version
							FROM v_product_series`

// ListProducts returns a list of products
func ListProductSeries(db *pgxpool.Pool) ([]ProductSeries, error) {
	pp := make([]ProductSeries, 0)
	if err := pgxscan.Select(context.Background(), db, &pp, listProductSeriesSQL); err != nil {
		return make([]ProductSeries, 0), err
	}
	return pp, nil
}
