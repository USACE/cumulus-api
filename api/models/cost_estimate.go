package models

import (
	"context"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

// DownloadEgressBytes returns the bytes served to users from download
// packages last retrieved in [from, to), i.e. size_bytes * retrieval_count as
// in the usage report. retrieval_count is cumulative with no per-fetch
// timestamps, so a package is attributed wholly to the period of its last
// retrieval.
func DownloadEgressBytes(ctx context.Context, db *pgxpool.Pool, from, to time.Time) (int64, error) {
	var b int64
	err := db.QueryRow(ctx,
		`SELECT COALESCE(SUM(size_bytes * retrieval_count), 0)::bigint
		 FROM download
		 WHERE last_retrieved_at >= $1 AND last_retrieved_at < $2`,
		from, to,
	).Scan(&b)
	return b, err
}
