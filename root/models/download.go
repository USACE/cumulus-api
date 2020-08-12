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
	ID              uuid.UUID  `json:"id"`
	DatetimeStart   time.Time  `json:"datetime_start" db:"datetime_start"`
	DatetimeEnd     time.Time  `json:"datetime_end" db:"datetime_end"`
	Progress        int16      `json:"progress"`
	File            *string    `json:"file"`
	ProcessingStart time.Time  `json:"processing_start" db:"processing_start"`
	ProcessingEnd   *time.Time `json:"processing_end" db:"processing_end"`
	DownloadStatus
}

// ListDownload returns all downloads from the database
func ListDownloads(db *sqlx.DB) ([]Download, error) {
	sql := `SELECT d.id,
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
	dd := make([]Download, 0)
	if err := db.Select(&dd, sql); err != nil {
		return make([]Download, 0), err
	}
	return dd, nil
}
