-- Lightweight display-name cache for admin usage reporting.
-- Populated on the fly from JWT claims (sub/preferred_username/email/name) as
-- users make authenticated requests -- not a re-introduction of app-owned identity.
CREATE TABLE IF NOT EXISTS user_directory (
    sub                 UUID PRIMARY KEY,
    preferred_username  VARCHAR(255),
    email               VARCHAR(255),
    name                VARCHAR(255),
    last_seen           TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Bytes of the completed package, extracted from Packager's manifest at completion time.
ALTER TABLE download ADD COLUMN IF NOT EXISTS size_bytes BIGINT;

-- Number of times the completed file was actually fetched (as opposed to the
-- download job merely being created), plus when that last happened.
ALTER TABLE download ADD COLUMN IF NOT EXISTS retrieval_count INTEGER NOT NULL DEFAULT 0;
ALTER TABLE download ADD COLUMN IF NOT EXISTS last_retrieved_at TIMESTAMPTZ;

-- One-time backfill for rows that predate this migration. Going forward,
-- size_bytes/retrieval_count are populated in application code (see
-- UpdateDownload / IncrementDownloadRetrieval); this only catches history.

-- The manifest already has the byte size for every completed download --
-- just extract it into the new column instead of leaving it NULL.
UPDATE download
SET size_bytes = (manifest ->> 'size_bytes')::bigint
WHERE size_bytes IS NULL
  AND manifest ? 'size_bytes'
  AND manifest ->> 'size_bytes' ~ '^\d+$';

-- Retrieval tracking didn't exist before this migration, so there's no way to
-- know the real historic count. Assume 1 for any download that actually
-- completed (SUCCESS/PARTIAL SUCCESS) rather than leaving it at the default
-- 0, which would understate usage for every pre-existing download.
UPDATE download d
SET retrieval_count = 1
FROM download_status s
WHERE d.status_id = s.id
  AND s.name IN ('SUCCESS', 'PARTIAL SUCCESS')
  AND d.retrieval_count = 0;
