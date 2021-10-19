
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
CREATE TRIGGER notify_acquirablefile_geoprocess
AFTER INSERT ON acquirablefile
FOR EACH ROW
EXECUTE PROCEDURE notify_acquirablefile_geoprocess();


--------------------------------------------------------------
-- ASYNC LISTENER FUNCTION (ALF) FOR snodas_interpolate_geoprocess
--------------------------------------------------------------

-- Trigger Function; Inserts Into acquirablefile Table
CREATE OR REPLACE FUNCTION notify_snodas_interpolate_geoprocess() RETURNS trigger AS $$
    BEGIN
        PERFORM (
            WITH geoprocess_config as (
                SELECT 
                       (SELECT config_value from config where config_name = 'write_to_bucket') AS bucket,
                       to_char(datetime, 'YYYYMMDD')  AS datetime,
                       CAST(16 as real)               AS max_distance
                FROM v_productfile
                WHERE id = NEW.id
                AND product_slug = 'nohrsc-snodas-swe'
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

-- Trigger; NOTIFY NEW ACQUIRABLEFILE ON INSERT
CREATE TRIGGER notify_snodas_interpolate_geoprocess
AFTER INSERT or UPDATE ON productfile
FOR EACH ROW
EXECUTE PROCEDURE notify_snodas_interpolate_geoprocess();