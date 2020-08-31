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

// DownloadUpdate struct
type DownloadUpdate struct {
	ID            uuid.UUID  `json:"id"`
	Progress      int16      `json:"progress"`
	StatusID      uuid.UUID  `json:"status_id" db:"status_id"`
	ProcessingEnd *time.Time `json:"processing_end" db:"processing_end"`
}

// ListDownloads returns all downloads from the database
func ListDownloads(db *sqlx.DB) ([]Download, error) {

	dd := make([]Download, 0)
	if err := db.Select(&dd, listDownloadSQL()); err != nil {
		return make([]Download, 0), err
	}
	return dd, nil
}

// CreateDownload creates a download record in
func CreateDownload(db *sqlx.DB, d Download) (*Download, error) {

	sql := `INSERT INTO download (datetime_start, datetime_end, status_id)
			VALUES ($1, $2, '94727878-7a50-41f8-99eb-a80eb82f737a')
			RETURNING *`

	var dNew Download
	if err := db.Get(&dNew, sql, d.DatetimeStart, d.DatetimeEnd); err != nil {
		return nil, err
	}

	//*****************
	//this is NOT FINAL
	//*****************
	dpSQL := `INSERT INTO download_product (product_id, download_id) VALUES ($1, $2) RETURNING id`
	for _, pID := range d.ProductID {

		var record []string
		if err := db.Select(&record, dpSQL, pID, dNew.ID); err != nil {
			return nil, err
		}
	}

	return &dNew, nil
}

// UpdateDownload is called by lamda function to update fields
func UpdateDownload(db *sqlx.DB, u *DownloadUpdate) ([]Download, error) {

	sql := `UPDATE download set progress = $2, status_id = $3, processing_end = $4
			WHERE id = $1
			RETURNING *`

	if u.Progress == 100 {
		t := time.Now()
		u.ProcessingEnd = &t
	}

	dd := make([]Download, 0)
	if err := db.Select(&dd, sql, u.ID, u.Progress, u.StatusID, u.ProcessingEnd); err != nil {
		return make([]Download, 0), err
	}
	return dd, nil
}

// GetDownload returns a single download record
func GetDownload(db *sqlx.DB, id *uuid.UUID) ([]Download, error) {

	dd := make([]Download, 0)
	if err := db.Select(&dd, listDownloadSQL()+" WHERE d.id = $1", id); err != nil {
		return make([]Download, 0), err
	}
	return dd, nil
}

func listDownloadSQL() string {
	return `SELECT d.id,
				d.datetime_start,
				d.datetime_end,
				d.progress,
				d.file,
				d.processing_start,
				d.processing_end,
				d.status_id,
				s.name AS status
				--dp.product_id
			FROM download d
			INNER JOIN download_status s ON d.status_id = s.id
			--INNER JOIN download_product dp on d.id = dp.download_id
`
}
