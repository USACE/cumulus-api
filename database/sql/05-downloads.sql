-- extensions
CREATE extension IF NOT EXISTS "uuid-ossp";


-- drop tables if they already exist
drop table if exists
    download,
    download_product,
    download_status
	CASCADE;


-- download_status_id
CREATE TABLE IF NOT EXISTS download_status (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(120) NOT NULL
);

-- download
CREATE TABLE IF NOT EXISTS download (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    datetime_start TIMESTAMPTZ NOT NULL,
    datetime_end TIMESTAMPTZ NOT NULL,
    progress INTEGER NOT NULL DEFAULT 0,
    status_id UUID REFERENCES download_status(id),
    watershed_id UUID REFERENCES watershed(id),
    file VARCHAR(240),
    processing_start TIMESTAMPTZ NOT NULL DEFAULT now(),
    processing_end TIMESTAMPTZ,
    profile_id UUID REFERENCES profile(id)
);

-- download_product
CREATE TABLE IF NOT EXISTS download_product (
    download_id UUID REFERENCES download(id),
    product_id UUID REFERENCES product(id),
    PRIMARY KEY (download_id, product_id)
);


-- -----
-- VIEWS
-- -----

CREATE OR REPLACE VIEW v_download AS (
        SELECT d.id AS id,
            d.datetime_start AS datetime_start,
            d.datetime_end AS datetime_end,
            d.progress AS progress,
            d.file AS file,
            d.processing_start AS processing_start,
            d.processing_end AS processing_end,
            d.status_id AS status_id,
            d.watershed_id AS watershed_id,
            d.profile_id AS profile_id,
            w.slug         AS watershed_slug,
            w.name         AS watershed_name,
            s.name AS status,
            dp.product_id AS product_id
        FROM download d
            INNER JOIN download_status s ON d.status_id = s.id
            INNER JOIN watershed w on w.id = d.watershed_id
            INNER JOIN (
                SELECT array_agg(product_id) as product_id,
                       download_id
                FROM download_product
                GROUP BY download_id
            ) dp ON d.id = dp.download_id
            ORDER BY d.processing_start DESC
    );

    -- v_download_request VIEW
    CREATE OR REPLACE VIEW v_download_request AS 
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
        FROM ( SELECT dp.download_id,
                    dp.product_id,
                    dp.datetime_start,
                    dp.datetime_end,
                    f.file AS key,
                    ( SELECT config.config_value
                        FROM config
                        WHERE config.config_name::text = 'write_to_bucket'::text) AS bucket,
                        CASE
                            WHEN p.temporal_duration = 0 THEN 'INST-VAL'::text
                            ELSE 'PER-CUM'::text
                        END AS dss_datatype,
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
                -- observed data will use the file datetime  
			  WHERE (date_part('year', f.version) = '1111' AND f.datetime >= dp.datetime_start AND f.datetime <= dp.datetime_end)
                -- forecast data with an end date < now (looking at forecasts in the past)
			    OR (dp.datetime_end < now() AND date_part('year', f.version) != '1111' AND f.version between dp.datetime_end - interval '12 hours' and dp.datetime_end)
			    -- forecast data with an end date >= now (looking at current latest forecasts)
			    OR (dp.datetime_end >= now() AND date_part('year', f.version) != '1111' AND f.version between now() - interval '12 hours' and now())
                ORDER BY f.product_id, f.version, f.datetime) dss;


-- ---------
-- SEED DATA
-- ---------

INSERT INTO download_status (id, name) VALUES
    ('94727878-7a50-41f8-99eb-a80eb82f737a', 'INITIATED'),
    ('3914f0bd-2290-42b1-bc24-41479b3a846f', 'SUCCESS'),
    ('a553101e-8c51-4ddd-ac2e-b011ed54389b', 'FAILED');