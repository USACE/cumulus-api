package models

import (
	"context"
	"sync"
	"time"

	// Postgres Database Driver
	"github.com/georgysavva/scany/v2/pgxscan"
	"github.com/google/uuid"
	_ "github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

// Productfile is a file associated with a product
type Productfile struct {
	ProductID     uuid.UUID  `json:"product_id" db:"product_id"`
	ID            uuid.UUID  `json:"id"`
	Datetime      time.Time  `json:"datetime"`
	File          string     `json:"file"`
	Version       *time.Time `json:"version"`
	AcquirablesID *uuid.UUID `json:"acquirablefile_id" db:"acquirablefile_id"`
}

type ProductfileAvailability struct {
	Datetime    time.Time `json:"datetime"`
	IsAvailable bool      `json:"is_available"`
}

// ProductfileCOG is a productfile exposed as a directly-readable, Range-capable
// COG proxy URL (served by StreamProductfileCOG) instead of a raw S3 key.
type ProductfileCOG struct {
	ID       uuid.UUID  `json:"id"`
	Datetime time.Time  `json:"datetime"`
	Version  *time.Time `json:"version"`
	CogURL   string     `json:"cog_url"`
}

// ProductfileObject is the S3 bucket + key backing a single productfile.
type ProductfileObject struct {
	Key    string `json:"key" db:"key"`
	Bucket string `json:"bucket" db:"bucket"`
}

// GetProductfileObject returns the S3 bucket and key for a productfile id.
// The bucket mirrors the download view: the 'write_to_bucket' config value; the
// key is the productfile.file column.
func GetProductfileObject(db *pgxpool.Pool, ID uuid.UUID) (*ProductfileObject, error) {
	var obj ProductfileObject
	if err := pgxscan.Get(
		context.Background(), db, &obj,
		`SELECT f.file AS key,
		        (SELECT config.config_value FROM config WHERE config.config_name::text = 'write_to_bucket'::text) AS bucket
		 FROM productfile f
		 WHERE f.id = $1`,
		ID,
	); err != nil {
		return nil, err
	}
	return &obj, nil
}

// --- Cached productfile -> {bucket, key} lookup ------------------------------------------------
//
// The COG proxy (StreamProductfileCOG) resolves the S3 bucket+key on EVERY Range request, and a
// single client import fires thousands of them. The mapping is immutable for a given productfile id
// (its file column never changes, and write_to_bucket is a process-constant config value), so it is
// safe to memoize — keeping the 15-connection Postgres pool out of the per-read hot path.

// productfileCacheMax bounds the in-memory key cache so a long-running process can't grow without
// limit. Entries are ~an id + a short key string; the cap is ~tens of MB.
const productfileCacheMax = 200000

var (
	pfCacheMu     sync.RWMutex
	pfCacheBucket string
	pfCacheKeys   = make(map[uuid.UUID]string)
)

// GetProductfileObjectCached returns the S3 bucket+key for a productfile id, memoized. On a miss it
// falls back to the database (one cheap scalar query); the write_to_bucket bucket is read once and
// reused. Safe for concurrent use.
func GetProductfileObjectCached(db *pgxpool.Pool, ID uuid.UUID) (*ProductfileObject, error) {
	pfCacheMu.RLock()
	key, keyOK := pfCacheKeys[ID]
	bucket := pfCacheBucket
	pfCacheMu.RUnlock()

	if keyOK && bucket != "" {
		return &ProductfileObject{Bucket: bucket, Key: key}, nil
	}

	// Resolve the bucket once (immutable config value).
	if bucket == "" {
		b, err := getWriteToBucket(db)
		if err != nil {
			return nil, err
		}
		bucket = b
		pfCacheMu.Lock()
		pfCacheBucket = b
		pfCacheMu.Unlock()
	}

	// Resolve + cache the key (immutable per id). A rare concurrent double-miss just queries twice
	// and stores the same value — harmless.
	if !keyOK {
		k, err := getProductfileKey(db, ID)
		if err != nil {
			return nil, err
		}
		key = k
		pfCacheMu.Lock()
		// Bound memory over a long uptime. Entries are immutable and cheap to repopulate, so a crude
		// drop-all on overflow is safe (subsequent reads simply re-query).
		if len(pfCacheKeys) >= productfileCacheMax {
			pfCacheKeys = make(map[uuid.UUID]string)
		}
		pfCacheKeys[ID] = k
		pfCacheMu.Unlock()
	}

	return &ProductfileObject{Bucket: bucket, Key: key}, nil
}

func getWriteToBucket(db *pgxpool.Pool) (string, error) {
	var bucket string
	err := db.QueryRow(
		context.Background(),
		`SELECT config_value FROM config WHERE config_name::text = 'write_to_bucket'::text`,
	).Scan(&bucket)
	return bucket, err
}

func getProductfileKey(db *pgxpool.Pool, ID uuid.UUID) (string, error) {
	var key string
	err := db.QueryRow(
		context.Background(),
		`SELECT file FROM productfile WHERE id = $1`,
		ID,
	).Scan(&key)
	return key, err
}

// ListProductfiles returns array of productfiles
func ListProductfiles(db *pgxpool.Pool, ID uuid.UUID, after string, before string) ([]Productfile, error) {
	ff := make([]Productfile, 0)
	if err := pgxscan.Select(
		context.Background(), db, &ff,
		`SELECT product_id, id, datetime, file, version, acquirablefile_id
	     FROM productfile
		 WHERE product_id = $1 AND datetime >= $2 AND datetime <= $3`,
		ID, after, before,
	); err != nil {
		return make([]Productfile, 0), err
	}
	return ff, nil
}

// ListProductfilesLatestVersion returns ONE productfile per valid time over the range — the latest
// forecast version for each datetime. A forecast product stores many issue-cycle versions of the
// same valid time (version = the real reference/issue time), which would otherwise yield several
// COGs per timestep; DISTINCT ON (datetime) ORDER BY version DESC keeps only the most-recent issue
// for each. Observed products use the '1111-11-11..' sentinel version (one row per datetime already),
// so this is effectively a pass-through for them. This is what the COG importer wants: one COG per
// timestep, not every version.
//
// Note: bounded by the datetime range, but an index on (product_id, datetime, version DESC) would
// make the DISTINCT ON cheap if this is ever run over very wide ranges.
func ListProductfilesLatestVersion(db *pgxpool.Pool, ID uuid.UUID, after string, before string) ([]Productfile, error) {
	ff := make([]Productfile, 0)
	if err := pgxscan.Select(
		context.Background(), db, &ff,
		`SELECT DISTINCT ON (datetime)
		        product_id, id, datetime, file, version, acquirablefile_id
		 FROM productfile
		 WHERE product_id = $1 AND datetime >= $2 AND datetime <= $3
		 ORDER BY datetime, version DESC`,
		ID, after, before,
	); err != nil {
		return make([]Productfile, 0), err
	}
	return ff, nil
}

func GetProductFileAvailability(db *pgxpool.Pool, ID uuid.UUID, interval string, d time.Time) ([]ProductfileAvailability, error) {
	avail := make([]ProductfileAvailability, 0)
	startTime := time.Date(d.Year(), d.Month(), d.Day(), 0, 0, 0, 0, d.Location()).Format(time.RFC3339)
	endTime := time.Date(d.Year(), d.Month(), d.Day(), 23, 0, 0, 0, d.Location()).Format(time.RFC3339)

	if interval == "24 Hour" {
		if err := pgxscan.Select(context.Background(), db, &avail,
			`SELECT datetime, TRUE as is_available
			FROM productfile
			WHERE product_id = $1 AND datetime >= $2 AND datetime <= $3
			ORDER BY datetime`, ID, startTime, endTime,
		); err != nil {
			return make([]ProductfileAvailability, 0), err
		}
		if len(avail) == 0 {
			avail = append(avail, ProductfileAvailability{
				Datetime:    time.Date(d.Year(), d.Month(), d.Day(), 0, 0, 0, 0, d.Location()),
				IsAvailable: false,
			})
		}
	} else {
		if err := pgxscan.Select(context.Background(), db, &avail,
			`WITH hours AS (
					SELECT generate_series(
							$1::timestamp,  -- Start of the interval
							$2::timestamp,  -- End of the interval
							$3::interval
					) AS hour
			)
			SELECT
					h.hour as datetime,
					CASE
							WHEN pf.datetime IS NOT NULL THEN TRUE
							ELSE FALSE
					END AS is_available
			FROM
					hours h
			LEFT JOIN (
				select * from productfile where product_id = $4 and datetime >= $5 and datetime <= $6
			) pf ON date_trunc('hour', pf.datetime) = h.hour
			ORDER BY
					h.hour`, startTime, endTime, interval, ID, startTime, endTime,
		); err != nil {
			return make([]ProductfileAvailability, 0), err
		}
	}
	return avail, nil
}

// CreateProductfiles creates productfiles from an array of productfiles
func CreateProductfiles(db *pgxpool.Pool, ff []Productfile) (int, error) {
	savedCount := 0
	tx, err := db.Begin(context.Background())
	if err != nil {
		return 0, err
	}
	defer tx.Rollback(context.Background())
	for _, f := range ff {
		if f.Version != nil {
			if _, err := tx.Exec(
				context.Background(),
				`INSERT INTO productfile (datetime, file, product_id, version, acquirablefile_id) VALUES ($1, $2, $3, $4, $5)
				 ON CONFLICT ON CONSTRAINT unique_product_version_datetime DO UPDATE SET update_date = CURRENT_TIMESTAMP`,
				f.Datetime, f.File, f.ProductID, f.Version, f.AcquirablesID,
			); err != nil {
				return 0, err
			}
		} else {
			if _, err := tx.Exec(
				context.Background(),
				`INSERT INTO productfile (datetime, file, product_id, acquirablefile_id) VALUES ($1, $2, $3, $4)
				 ON CONFLICT ON CONSTRAINT unique_product_version_datetime DO UPDATE SET update_date = CURRENT_TIMESTAMP`,
				f.Datetime, f.File, f.ProductID, f.AcquirablesID,
			); err != nil {
				return 0, err
			}
		}
		savedCount += 1
	}
	err = tx.Commit(context.Background())
	if err != nil {
		return 0, err
	}
	return savedCount, nil
}
