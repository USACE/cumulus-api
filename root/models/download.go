package models

import (
	"time"

	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
)

// DownloadStatus is status of a download
type DownloadStatus struct {
	StatusID uuid.UUID `json:"status_id" db:"status_id"`
	Status   string    `json:"status"`
}

// Download is a
type Download struct {
	ID              uuid.UUID   `json:"id"`
	DatetimeStart   time.Time   `json:"datetime_start" db:"datetime_start"`
	DatetimeEnd     time.Time   `json:"datetime_end" db:"datetime_end"`
	Progress        int16       `json:"progress"`
	File            *string     `json:"file"`
	ProcessingStart time.Time   `json:"processing_start" db:"processing_start"`
	ProcessingEnd   *time.Time  `json:"processing_end" db:"processing_end"`
	ProductID       []uuid.UUID `json:"product_id"`
	DownloadStatus
}

// ListDownload returns all downloads from the database
func ListDownloads(db *sqlx.DB) ([]Download, error) {

	dd := make([]Download, 0)
	if err := db.Select(&dd, listDownloadSQL()); err != nil {
		return make([]Download, 0), err
	}
	return dd, nil
}

// CreateDownload creates a download record in
func CreateDownload(db *sqlx.DB) ([]Download, error) {

	sql := `INSERT INTO download (id, datetime_start, datetime_end, 
				geom, progress, status_id, file, processing_start, processing_end)
			VALUES (DEFAULT, '2020-08-12', '2020-08-14', null, 0, '94727878-7a50-41f8-99eb-a80eb82f737a', 
				'testfile.dss', now(), null) RETURNING id, datetime_start, datetime_end, progress, status_id,
				processing_start`

	dd := make([]Download, 0)
	if err := db.Select(&dd, sql); err != nil {
		return make([]Download, 0), err
	}
	return dd, nil
}

func GetDownload(db *sqlx.DB, id *uuid.UUID) ([]Download, error) {

	dd := make([]Download, 0)
	if err := db.Select(&dd, listDownloadSQL()+" WHERE d.id = $1", id); err != nil {
		return make([]Download, 0), err
	}
	return dd, nil

	// var t ts.Timeseries
	// if err := db.Get(&t, listTimeseriesSQL()+" WHERE T.id = $1", id); err != nil {
	// 	return nil, err
	// }
	// return &t, nil

}

func listDownloadSQL() string {
	return `SELECT d.id,
				d.datetime_start,
				d.datetime_end,
				d.progress,
				d.file,
				d.processing_start,
				d.processing_end,
				s.name AS status
			FROM download d
			INNER JOIN download_status s ON d.status_id = s.id
`
}
