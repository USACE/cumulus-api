
-------------------------
-- FUNCTIONS AND TRIGGERS
-------------------------

-- Async Listener Function JSON Format
-- {
--   "fn": "new-download",
--   "details": "{\"geoprocess\" : \"inco...}"
-- }
-- Note: ^^^ value of "details": must be a string. A native JSON object for "details" can be converted
-- to a string using Postgres type casting, for example: json_build_object('id', NEW.id)::text
-- will produce string like "{\"id\" : \"f1105618-047e-40bc-bd2e-961ad0e05084\"}"
-- where required JSON special characters are escaped.


-- Shared Function to Notify Cumulus Async Listener Functions (ALF) Listener
CREATE OR REPLACE FUNCTION notify_async_listener(t text) RETURNS void AS $$
    BEGIN
        PERFORM (SELECT pg_notify('cumulus_new', t));
    END;
$$ LANGUAGE plpgsql;


------------------------------------------------------------
-- ASYNC LISTENER FUNCTION (ALF) FOR packager (dss download)
------------------------------------------------------------

-- Trigger Function; Inserts Into Download Table (New File Needed from Packager)
CREATE OR REPLACE FUNCTION notify_new_download() RETURNS trigger AS $$
    BEGIN
        PERFORM (
            SELECT notify_async_listener(
                json_build_object(
                    'fn',     'new-download',
                    'details', json_build_object('id', NEW.id)::text
                )::text
			)
		);
        RETURN NULL;
    END;
$$ LANGUAGE plpgsql;

-- Trigger; NOTIFY NEW DOWNLOAD ON INSERT
-- DROP first: this is a repeatable migration, so it re-runs whenever its checksum changes and a
-- bare CREATE TRIGGER would fail with "trigger already exists". The file had never been edited
-- since it was introduced, so it had never re-run and the missing guards had never surfaced.
DROP TRIGGER IF EXISTS notify_new_download ON download;
CREATE TRIGGER notify_new_download
AFTER INSERT ON download
FOR EACH ROW
EXECUTE PROCEDURE notify_new_download();


--------------------------------------------------------------
-- ASYNC LISTENER FUNCTION (ALF) FOR acquirablefile_geoprocess
--------------------------------------------------------------

-- Trigger Function; Inserts Into acquirablefile Table
CREATE OR REPLACE FUNCTION notify_acquirablefile_geoprocess() RETURNS trigger AS $$
    BEGIN
        PERFORM (
            WITH geoprocess_config as (
                SELECT id                        AS acquirablefile_id,
                       acquirable_id             AS acquirable_id,
                       acquirable_slug           AS acquirable_slug,
                       (SELECT config_value from config where config_name = 'write_to_bucket') AS bucket,
                       file                      AS key
                FROM v_acquirablefile
                WHERE id = NEW.id
            )
            SELECT notify_async_listener(
                json_build_object(
                    'fn', 'geoprocess-acquirablefile',
                    'details', json_build_object(
                        'geoprocess', 'incoming-file-to-cogs',
                        'geoprocess_config', row_to_json(geoprocess_config)
                    )::text
                )::text
            ) FROM geoprocess_config
        );
        RETURN NULL;
    END;
$$ LANGUAGE plpgsql;

-- Trigger; NOTIFY NEW ACQUIRABLEFILE ON INSERT
DROP TRIGGER IF EXISTS notify_acquirablefile_geoprocess ON acquirablefile;
CREATE TRIGGER notify_acquirablefile_geoprocess
AFTER INSERT ON acquirablefile
FOR EACH ROW
EXECUTE PROCEDURE notify_acquirablefile_geoprocess();


--------------------------------------------------------------
-- ASYNC LISTENER FUNCTION (ALF) FOR snodas_interpolate_geoprocess
--------------------------------------------------------------

-- Trigger Function; NOTIFY snodas-interpolate geoprocess for a new SNODAS SWE productfile
--
-- Reads 'product' directly instead of going through v_productfile. v_productfile LEFT JOINs
-- v_product, and v_product carries an unfiltered
--     SELECT product_id, COUNT(id), MIN(datetime), MAX(datetime), max(version)
--     FROM productfile GROUP BY product_id
-- rollup. The product_slug test only resolves to a product id at execution time, so the planner
-- could not push a constant into that grouped subquery -- and v_product's own ORDER BY blocks
-- subquery pull-up -- leaving it to aggregate the ENTIRE productfile table and then join a
-- single row against the result. Since this trigger is FOR EACH ROW on INSERT OR UPDATE, that
-- full-table aggregate ran once per ingested file. CreateProductfiles inserts a row per
-- statement with ON CONFLICT DO UPDATE, so re-ingesting an existing file paid it as well.
--
-- Everything the payload needs is already on NEW (datetime, product_id), so the only lookup
-- left is a primary-key hit on the small product table.
--
-- 'NOT p.deleted' preserves the previous behaviour: v_product filters deleted products, so a
-- productfile belonging to a deleted product came back with product_slug = NULL through the
-- LEFT JOIN and never matched the slug test.
CREATE OR REPLACE FUNCTION notify_snodas_interpolate_geoprocess() RETURNS trigger AS $$
    BEGIN
        PERFORM (
            WITH geoprocess_config as (
                SELECT
                       (SELECT config_value from config where config_name = 'write_to_bucket') AS bucket,
                       to_char(NEW.datetime, 'YYYYMMDD')  AS datetime,
                       CAST(16 as real)                   AS max_distance
                FROM product p
                WHERE p.id = NEW.product_id
                  AND p.slug = 'nohrsc-snodas-swe'
                  AND NOT p.deleted
            )
            SELECT notify_async_listener(
                json_build_object(
                    'fn', 'geoprocess-snodas-interpolate',
                    'details', json_build_object(
                        'geoprocess', 'snodas-interpolate',
                        'geoprocess_config', row_to_json(geoprocess_config)
                    )::text
                )::text
            ) FROM geoprocess_config
        );
        RETURN NULL;
    END;
$$ LANGUAGE plpgsql;

-- Trigger; NOTIFY NEW SNODAS SWE PRODUCTFILE ON INSERT OR UPDATE
DROP TRIGGER IF EXISTS notify_snodas_interpolate_geoprocess ON productfile;
CREATE TRIGGER notify_snodas_interpolate_geoprocess
AFTER INSERT or UPDATE ON productfile
FOR EACH ROW
EXECUTE PROCEDURE notify_snodas_interpolate_geoprocess();