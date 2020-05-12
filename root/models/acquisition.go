package models

import (
	"encoding/json"
	"log"

	"api/root/acquisition"
	"api/root/asyncfn"

	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
)

// AcquirableInfo stores common data for an Acquirable
type AcquirableInfo struct {
	ID       uuid.UUID `json:"id"`
	Name     string    `json:"name"`
	Schedule string    `json:"schedule"`
}

// Acquisition is a data retrieval request
type Acquisition struct {
	ID       uuid.UUID `json:"id"`
	Datetime string    `json:"datetime"`
}

// AcquirableAcquisition is the acquisition of an acquirable
type AcquirableAcquisition struct {
	ID            uuid.UUID `json:"id"`
	AcquisitionID uuid.UUID `json:"acquisition_id" db:"acquisition_id"`
	AcquirableID  uuid.UUID `json:"acquirable_id"`
}

// Acquirable interface
type Acquirable interface {
	URLS() []string
	Info() *AcquirableInfo
}

// ListAcquirables returns AcquirableInfo from the database
func ListAcquirables(db *sqlx.DB) ([]AcquirableInfo, error) {
	aa := make([]AcquirableInfo, 0)
	if err := db.Select(&aa, `SELECT * FROM ACQUIRABLE`); err != nil {
		return make([]AcquirableInfo, 0), err
	}
	return aa, nil
}

// Acquirables converts all acquirables from the database to
// their concrete type to support the Acquirable interface
func Acquirables(db *sqlx.DB) ([]Acquirable, error) {

	aa, err := ListAcquirables(db)
	if err != nil {
		return make([]Acquirable, 0), err
	}

	var acquirables []Acquirable
	for _, a := range aa {
		acquirables = append(acquirables, AcquirableFactory(&a))
	}

	return acquirables, nil
}

// CreateAcquisition creates a acquisiton record and triggers downloads
func CreateAcquisition(db *sqlx.DB) (Acquisition, error) {

	txn := db.MustBegin()
	sql := `INSERT INTO acquisition DEFAULT VALUES
			RETURNING id, datetime
	`

	// Create record of acquisition in database
	var acq Acquisition
	if err := txn.QueryRowx(sql).StructScan(&acq); err != nil {
		txn.Rollback()
		return Acquisition{}, err
	}

	// Get Acquirables
	aa, err := Acquirables(db)
	if err != nil {
		txn.Rollback()
		return Acquisition{}, err
	}

	// Check each to see if cron should run
	for _, a := range aa {
		if acquisition.CronShouldRunNow(a.Info().Schedule, "5m") {
			// Create AquirableAcquisition
			if err = CreateAcquirableAcquisition(
				db,
				AcquirableAcquisition{AcquirableID: a.Info().ID, AcquisitionID: acq.ID},
			); err != nil {
				log.Printf(err.Error())
			}

			// Fire Acquisition Event for each URL
			payload, err := json.Marshal(a)
			if err != nil {
				txn.Rollback()
				return Acquisition{}, err
			}

			// Invoke AWS Lambda
			if err := asyncfn.CallAsync(
				"corpsmap-cumulus-downloader",
				payload,
			); err != nil {
				txn.Rollback()
				return Acquisition{}, err
			}

		}
	}

	txn.Commit()
	return acq, nil
}

// CreateAcquirableAcquisition creates a record of an acquirable being acquired
func CreateAcquirableAcquisition(db *sqlx.DB, a AcquirableAcquisition) error {

	if _, err := db.Exec(
		`INSERT INTO acquirable_acquisition (acquisition_id, acquirable_id) VALUES ($1, $2)`,
		a.AcquisitionID, a.AcquirableID,
	); err != nil {
		return err
	}

	return nil
}
