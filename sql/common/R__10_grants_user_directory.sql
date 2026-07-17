-- Repeatable migration to ensure user_directory permissions are always correct.
-- Runs every time migrations are applied. The user_directory table is written
-- (upserted) on every authenticated request and read by the admin usage
-- endpoints, so the API role (cumulus_user) needs read + write access.

GRANT USAGE ON SCHEMA cumulus TO cumulus_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON cumulus.user_directory TO cumulus_user;

DO $$
BEGIN
    RAISE NOTICE 'Granted user_directory permissions to cumulus_user';
END
$$;
