package models

import (
	"encoding/json"
	"fmt"
	"log"
	"strings"

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
	AcquirableID  uuid.UUID `json:"acquirable_id" db:"acquirable_id"`
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

// CreateAcquisition creates a acquisiton record in the database
func CreateAcquisition(db *sqlx.DB) (Acquisition, error) {

	sql := `INSERT INTO acquisition DEFAULT VALUES
			RETURNING id, datetime
	`

	// Create record of acquisition in database
	var acq Acquisition
	if err := db.QueryRowx(sql).StructScan(&acq); err != nil {
		return Acquisition{}, err
	}
	return acq, nil
}

// DoAcquire creates a new acquisition and triggers acquisition functions
func DoAcquire(db *sqlx.DB) (Acquisition, error) {

	// Create a new Acquisition
	acq, err := CreateAcquisition(db)
	if err != nil {
		return acq, err
	}

	// Start a transaction
	txn := db.MustBegin()

	// Get Acquirables
	aa, err := Acquirables(db)
	if err != nil {
		txn.Rollback()
		return acq, err
	}

	// Check if Cron should run for each acquirable
	for _, a := range aa {
		log.Printf("Checking cron for Acquirable %s : %s", a.Info().ID, a.Info().Name)
		if acquisition.CronShouldRunNow(a.Info().Schedule, "5m") {
			// Create AquirableAcquisition
			if err = CreateAcquirableAcquisition(
				db,
				AcquirableAcquisition{AcquisitionID: acq.ID, AcquirableID: a.Info().ID},
			); err != nil {
				log.Printf(err.Error())
			}

			// Fire Acquisition Event for each URL
			for _, url := range a.URLS() {
				urlSplit := strings.Split(url, "/")
				payload, err := json.Marshal(
					map[string]string{
						"key": fmt.Sprintf("cumulus/%s/%s", a.Info().Name, urlSplit[len(urlSplit)-1]),
						"url": url,
					},
				)
				if err != nil {
					txn.Rollback()
					return acq, err
				}
				// Invoke AWS Lambda
				if err := asyncfn.CallAsync(
					"corpsmap-cumulus-downloader",
					payload,
				); err != nil {
					txn.Rollback()
					return acq, err
				}
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
