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
CREATE OR REPLACE VIEW v_download_request AS (
    WITH download_products AS (
        SELECT dp.download_id,
            dp.product_id,
            d.datetime_start,
            d.datetime_end
        FROM download d
        JOIN download_product dp ON dp.download_id = d.id
    )
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
    FROM (
        SELECT dp.download_id,
               dp.product_id,
               dp.datetime_start,
               dp.datetime_end,
               f.file AS key,
               (SELECT config.config_value FROM config WHERE config.config_name::text = 'write_to_bucket'::text) AS bucket,
               d.name AS dss_datatype,
               CASE
                   WHEN p.temporal_duration = 0 THEN f.datetime
                   ELSE f.datetime - p.temporal_duration::double precision * '00:00:01'::interval
               END AS datetime_dss_dpart,
               CASE
                   WHEN p.temporal_duration = 0 THEN NULL::timestamp with time zone
                   ELSE f.datetime
               END AS datetime_dss_epart,
               p.dss_fpart,
               u.name AS dss_unit,
               a.name AS dss_cpart,
               f.version AS forecast_version
        FROM productfile f
        JOIN download_products dp ON dp.product_id = f.product_id
        JOIN product p ON f.product_id = p.id
        JOIN unit u ON p.unit_id = u.id
        JOIN parameter a ON a.id = p.parameter_id
        JOIN dss_datatype d ON p.dss_datatype_id = d.id
        -- Observed rows carry a year-1111 sentinel in 'version'; forecast rows carry the real
        -- issue/reference time. The test is written as a range against 1900 rather than
        -- date_part('year', f.version) = '1111' so it is sargable: wrapping the column in a
        -- function makes it opaque to unique_product_version_datetime (product_id, version,
        -- datetime), which then restricts on product_id only and filters every row of the
        -- product's history. As a range it uses the version key too.
        --
        -- A range is also required for correctness -- there is NOT one sentinel value. Production
        -- holds at least three distinct year-1111 values (1111-11-04 11:04:09.11+00 on the
        -- majority of rows, 1111-11-11 11:11:11.11+00, and 1111-11-03 23:52:58+00), so matching
        -- the nominal sentinel by equality would misclassify most observed rows as forecasts.
        -- Nothing below 1900 is a real forecast issue time, so the cutoff is safe.
        -- observed data will use the file datetime
        WHERE (f.version < '1900-01-01'::timestamptz AND f.datetime >= dp.datetime_start AND f.datetime <= dp.datetime_end)
        -- forecast data with an end date < now (looking at forecasts in the past)
        OR (dp.datetime_end < now() AND f.version >= '1900-01-01'::timestamptz AND f.version between dp.datetime_end - interval '24 hours' and dp.datetime_end)
        -- forecast data with an end date >= now (looking at current latest forecasts)
        OR (dp.datetime_end >= now() AND f.version >= '1900-01-01'::timestamptz AND f.version between now() - interval '18 hours' and now())
        ORDER BY f.product_id, f.version, f.datetime
    ) dss
);

GRANT SELECT ON
    v_download,
    v_download_request
TO cumulus_reader;
