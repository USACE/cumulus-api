-- Always re-apply when running migrations: ${flyway:timestamp}
-- Dropped and recreated (not just CREATE OR REPLACE) because this revision
-- renames a column (file -> raw_file) and inserts new columns mid-list;
-- CREATE OR REPLACE VIEW only allows appending columns, so it would error on
-- any existing deployment. Nothing depends on v_download, so no CASCADE.
DROP VIEW IF EXISTS v_download;
CREATE OR REPLACE VIEW v_download AS (
    SELECT d.id            AS id,
        d.datetime_start   AS datetime_start,
        d.datetime_end     AS datetime_end,
        d.progress         AS progress,
        d.file             AS raw_file,
        d.processing_start AS processing_start,
        d.processing_end   AS processing_end,
        d.status_id        AS status_id,
        d.watershed_id     AS watershed_id,
        d.sub              AS sub,
        w.slug             AS watershed_slug,
        w.name             AS watershed_name,
        s.name             AS status,
        dp.product_id      AS product_id,
        f.abbreviation     AS format,
        d.manifest         AS manifest,
        d.clip_geojson     AS clip_geojson,
        d.clip_region_name AS clip_region_name,
        d.size_bytes       AS size_bytes,
        d.retrieval_count  AS retrieval_count,
        d.last_retrieved_at AS last_retrieved_at,
        -- Return either custom clip region bbox or watershed bbox
        CASE 
            WHEN d.clip_geojson IS NOT NULL THEN
                ARRAY[
                    ST_XMin(ST_Transform(ST_GeomFromGeoJSON(d.clip_geojson), 5070))::FLOAT,
                    ST_YMin(ST_Transform(ST_GeomFromGeoJSON(d.clip_geojson), 5070))::FLOAT,
                    ST_XMax(ST_Transform(ST_GeomFromGeoJSON(d.clip_geojson), 5070))::FLOAT,
                    ST_YMax(ST_Transform(ST_GeomFromGeoJSON(d.clip_geojson), 5070))::FLOAT
                ]
            WHEN w.geometry IS NOT NULL THEN
                ARRAY[
                    ST_XMin(w.geometry)::FLOAT,
                    ST_YMin(w.geometry)::FLOAT,
                    ST_XMax(w.geometry)::FLOAT,
                    ST_YMax(w.geometry)::FLOAT
                ]
            ELSE NULL
        END AS clip_bbox,
        -- Return the clip region name
        CASE
            WHEN d.clip_geojson IS NOT NULL THEN
                COALESCE(d.clip_region_name, 'Custom Region')
            ELSE
                w.name
        END AS clip_name
    FROM download d
        INNER JOIN download_format f ON f.id = d.download_format_id
        INNER JOIN download_status s ON d.status_id = s.id
        LEFT JOIN watershed w on w.id = d.watershed_id
        INNER JOIN (
            SELECT array_agg(product_id) as product_id,
                    download_id
            FROM download_product
            GROUP BY download_id
        ) dp ON d.id = dp.download_id
        ORDER BY d.processing_start DESC
);

-- v_download_request
--
-- One row per productfile that belongs in a download's package: the S3 key to fetch, plus the DSS
-- metadata that grid will be written under.
--
-- The three match rules (observed / forecast-in-the-past / forecast-through-now) are written as
-- UNION ALL branches rather than one OR'd WHERE. They are mutually exclusive by construction --
-- the first tests version < 1900 and the other two version >= 1900, and those two are split on
-- datetime_end < now() vs >= now() -- so UNION ALL cannot produce duplicates, and it avoids the
-- sort that UNION would add to deduplicate.
--
-- The split is what makes the productfile access sargable. Every date bound in every rule comes
-- from the download row (dp.datetime_start / dp.datetime_end), so they are join quals, not
-- constants -- and the second rule's 'dp.datetime_end < now()' references only the download side.
-- An OR arm that depends on outer-relation-only conditions cannot be reduced to index quals on
-- productfile, so as a single OR the whole predicate had to be evaluated as a post-fetch Filter:
-- the only usable index qual was f.product_id, and each product's entire ingest history was read
-- from the heap and then discarded down to the requested window. Cost scaled with how long a
-- product had been ingested rather than with the window asked for. Split into branches, each gets
-- its own parameterized index scan and non-matching rows are rejected without a heap fetch.
--
-- The output column list is unchanged, so CREATE OR REPLACE is sufficient here -- no DROP needed
-- (unlike v_download above, which renamed a column).
CREATE OR REPLACE VIEW v_download_request AS (
    -- NOT MATERIALIZED is load-bearing, not cosmetic. This CTE is now referenced three times, and
    -- Postgres materializes a multiply-referenced CTE by default -- which would compute every
    -- download x product pair in the database before the caller's WHERE download_id = $1 could be
    -- applied. Inlining keeps that qual pushable into all three branches.
    WITH download_products AS NOT MATERIALIZED (
        SELECT dp.download_id,
            dp.product_id,
            d.datetime_start,
            d.datetime_end
        FROM download d
        JOIN download_product dp ON dp.download_id = d.id
    ),
    -- Match productfile rows first; the lookup tables are joined once against the narrowed set
    -- (in 'dss' below) rather than three times, once per branch.
    matched AS (
        -- Observed data: year-1111 sentinel version, selected on the file's own valid time.
        --
        -- The sentinel test is a range against 1900 rather than date_part('year', f.version) =
        -- '1111' both for sargability -- wrapping the column in a function makes it opaque to any
        -- index -- and for correctness: there is NOT one sentinel value. Production holds at least
        -- three distinct year-1111 values (1111-11-04 11:04:09.11+00 on the majority of rows,
        -- 1111-11-11 11:11:11.11+00, and 1111-11-03 23:52:58+00), so matching the nominal sentinel
        -- by equality would misclassify most observed rows as forecasts. Nothing below 1900 is a
        -- real forecast issue time, so the cutoff is safe.
        SELECT dp.download_id, dp.product_id, dp.datetime_start, dp.datetime_end,
               f.file, f.datetime, f.version
        FROM download_products dp
        JOIN productfile f
          ON f.product_id = dp.product_id
         AND f.datetime  >= dp.datetime_start
         AND f.datetime  <= dp.datetime_end
        WHERE f.version < '1900-01-01'::timestamptz

        UNION ALL

        -- Forecast data, requested window ends in the past: the issue cycles covering the 24 hours
        -- up to the end of the window.
        SELECT dp.download_id, dp.product_id, dp.datetime_start, dp.datetime_end,
               f.file, f.datetime, f.version
        FROM download_products dp
        JOIN productfile f
          ON f.product_id = dp.product_id
         AND f.version >= dp.datetime_end - interval '24 hours'
         AND f.version <= dp.datetime_end
        WHERE f.version >= '1900-01-01'::timestamptz
          AND dp.datetime_end < now()

        UNION ALL

        -- Forecast data, requested window reaches the present: the latest issue cycles.
        SELECT dp.download_id, dp.product_id, dp.datetime_start, dp.datetime_end,
               f.file, f.datetime, f.version
        FROM download_products dp
        JOIN productfile f
          ON f.product_id = dp.product_id
         AND f.version >= now() - interval '18 hours'
         AND f.version <= now()
        WHERE f.version >= '1900-01-01'::timestamptz
          AND dp.datetime_end >= now()
    ),
    dss AS (
        SELECT m.download_id,
               m.product_id,
               m.datetime_start,
               m.datetime_end,
               m.file AS key,
               (SELECT config.config_value FROM config WHERE config.config_name::text = 'write_to_bucket'::text) AS bucket,
               d.name AS dss_datatype,
               CASE
                   WHEN p.temporal_duration = 0 THEN m.datetime
                   ELSE m.datetime - p.temporal_duration::double precision * '00:00:01'::interval
               END AS datetime_dss_dpart,
               CASE
                   WHEN p.temporal_duration = 0 THEN NULL::timestamp with time zone
                   ELSE m.datetime
               END AS datetime_dss_epart,
               p.dss_fpart,
               u.name AS dss_unit,
               a.name AS dss_cpart,
               m.version AS forecast_version
        FROM matched m
        JOIN product p      ON p.id = m.product_id
        JOIN unit u         ON u.id = p.unit_id
        JOIN parameter a    ON a.id = p.parameter_id
        JOIN dss_datatype d ON d.id = p.dss_datatype_id
    )
    -- No ORDER BY. The previous definition sorted by (product_id, version, datetime) inside the
    -- view and nothing depended on it: the only caller re-sorts in
    -- jsonb_agg(... ORDER BY dss_fpart, key) -- see GetDownloadPackagerRequest in
    -- api/models/download.go -- and the dense_rank() window there supplies its own ordering.
    SELECT dss.download_id,
        dss.product_id,
        dss.datetime_start,
        dss.datetime_end,
        dss.key,
        dss.bucket,
        dss.dss_datatype,
        dss.dss_cpart,
        CASE
            WHEN dss.dss_datatype = 'INST-VAL'::text AND date_part('hour'::text, dss.datetime_dss_dpart) = 0::double precision 
                AND date_part('minute'::text, dss.datetime_dss_dpart) = 0::double precision 
            THEN to_char(dss.datetime_dss_dpart - '1 day'::interval, 'DDMONYYYY:24MI'::text)
            ELSE COALESCE(to_char(dss.datetime_dss_dpart, 'DDMONYYYY:HH24MI'::text), ''::text)
        END AS dss_dpart,
        CASE
            WHEN date_part('hour'::text, dss.datetime_dss_epart) = 0::double precision 
                AND date_part('minute'::text, dss.datetime_dss_dpart) = 0::double precision 
            THEN to_char(dss.datetime_dss_epart - '1 day'::interval, 'DDMONYYYY:24MI'::text)
            ELSE COALESCE(to_char(dss.datetime_dss_epart, 'DDMONYYYY:HH24MI'::text), ''::text)
        END AS dss_epart,
        dss.dss_fpart,
        dss.dss_unit,
        dss.forecast_version
    FROM dss
);

GRANT SELECT ON
    v_download,
    v_download_request
TO cumulus_reader;
