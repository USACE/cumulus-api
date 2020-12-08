package models

import (
	"encoding/json"

	"github.com/USACE/go-simple-asyncer/asyncer"

	"github.com/jmoiron/sqlx"
)

// DoStatistics creates a new acquisition and triggers acquisition functions
func DoStatistics(db *sqlx.DB, ae asyncer.Asyncer) error {

	// Check if Cron should run for each acquirable
	payload, err := json.Marshal(
		map[string]string{
			"s3_bucket": "corpsmap-data",
			"s3_key":    "cumulus/ncep_mrms_v12_MultiSensor_QPE_01H_Pass1/MRMS_MultiSensor_QPE_01H_Pass1_00.00_20201106-130000.tif",
			"vector":    "redrivernorth.shp",
		},
	)
	if err != nil {
		return err
	}
	// Async Call
	if err := ae.CallAsync(payload); err != nil {
		return err
	}

	return nil
}
