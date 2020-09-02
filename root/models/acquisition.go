package models

import (
	"encoding/json"
	"fmt"
	"log"
	"strings"

	"api/root/acquirable"
	"api/root/acquisition"
	"api/root/asyncer"

	"github.com/jmoiron/sqlx"
)

// ListAcquirableInfo returns acquirable.Info from the database
func ListAcquirableInfo(db *sqlx.DB) ([]acquirable.Info, error) {
	nn := make([]acquirable.Info, 0)
	if err := db.Select(&nn, `SELECT * FROM ACQUIRABLE`); err != nil {
		return make([]acquirable.Info, 0), err
	}
	return nn, nil
}


// ListAcquirables returns acquirable.Info from the database
func ListAcquirables(db *sqlx.DB) ([]acquirable.Acquirable, error) {

	nn, err := ListAcquirableInfo(db)
	if err != nil {
		return make([]acquirable.Acquirable, 0), err
	}

	// Create Concrete Types
	aa := make([]acquirable.Acquirable, len(nn))
	for idx := range nn {
		// Concrete type from info
		a, err := acquirable.Factory(nn[idx])
		if err != nil {
			return make([]acquirable.Acquirable, 0), err
		}
		aa[idx] = a
	}

	return aa, nil
}

// CreateAcquisitionAttempt creates a acquisiton record in the database
func CreateAcquisitionAttempt(db *sqlx.DB) (acquirable.AcquisitionAttempt, error) {

	sql := `INSERT INTO acquisition DEFAULT VALUES
			RETURNING id, datetime
	`

	// Create record of acquisition in database
	var a acquirable.AcquisitionAttempt
	if err := db.QueryRowx(sql).StructScan(&a); err != nil {
		return acquirable.AcquisitionAttempt{}, err
	}
	return a, nil
}

// DoAcquire creates a new acquisition and triggers acquisition functions
func DoAcquire(db *sqlx.DB, ae asyncer.Asyncer) (*acquirable.AcquisitionAttempt, error) {

	// Create a new Acquisition
	acq, err := CreateAcquisitionAttempt(db)
	if err != nil {
		return nil, err
	}

	// Start a transaction
	txn := db.MustBegin()

	// Get Acquirables
	aa, err := ListAcquirables(db)
	if err != nil {
		txn.Rollback()
		return nil, err
	}

	// Check if Cron should run for each acquirable
	for _, a := range aa {
		log.Printf("Checking cron for Acquirable %s : %s", a.Info().ID, a.Info().Name)

		if acquisition.CronShouldRunNow(a.Info().Schedule, "5m") {
			// Create AquirableAcquisition
			if err := CreateAcquirableAcquisition(
				db,
				acquirable.Acquisition{AcquisitionID: acq.ID, AcquirableID: a.Info().ID},
			); err != nil {
				log.Printf(err.Error())
			}

			// Fire Acquisition Event for each URL
			for _, url := range a.URLS() {
				urlSplit := strings.Split(url, "/")
				payload, err := json.Marshal(
					map[string]string{
						"s3_bucket": "corpsmap-data-incoming",
						"s3_key":    fmt.Sprintf("cumulus/%s/%s", a.Info().Name, urlSplit[len(urlSplit)-1]),
						"url":       url,
					},
				)
				if err != nil {
					txn.Rollback()
					return &acq, err
				}
				// Invoke AWS Lambda
				if err := ae.CallAsync(
					"corpsmap-cumulus-downloader",
					payload,
				); err != nil {
					txn.Rollback()
					return &acq, err
				}
			}
		}
	}

	txn.Commit()

	return &acq, nil
}

// CreateAcquirableAcquisition creates a record of an acquirable being acquired
func CreateAcquirableAcquisition(db *sqlx.DB, a acquirable.Acquisition) error {

	if _, err := db.Exec(
		`INSERT INTO acquirable_acquisition (acquisition_id, acquirable_id) VALUES ($1, $2)`,
		a.AcquisitionID, a.AcquirableID,
	); err != nil {
		return err
	}

	return nil
}
