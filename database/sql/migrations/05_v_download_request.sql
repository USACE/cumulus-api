SET search_path TO cumulus,topology,tiger,tiger_data,public;

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
                WHERE f.datetime >= dp.datetime_start AND f.datetime <= dp.datetime_end
                ORDER BY f.product_id, f.version, f.datetime) dss;

-- Apply roles
GRANT SELECT ON
    v_download_request
TO cumulus_reader;

-- Fix WRF forecast_version to '1111-11-11'
-- WRF Precip
UPDATE product set forecast_version = '1111-11-11' where id = 'b50f29f4-547b-4371-9365-60d44eef412e'
-- WRF AirTemp
UPDATE product set forecast_version = '1111-11-11' where id = '793e285f-333b-41a3-b4ab-223a7a764668'