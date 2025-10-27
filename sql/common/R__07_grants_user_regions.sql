-- Repeatable migration to ensure user_region permissions are always correct
-- This runs every time migrations are applied to ensure permissions are set

-- DEBUG: Show Flyway migration history in logs
DO $$
DECLARE
    migration_history TEXT;
BEGIN
    SELECT string_agg(
        format('installed_rank: %s | version: %s | description: %s | type: %s | script: %s | checksum: %s | installed_on: %s | execution_time: %s | success: %s',
            installed_rank,
            COALESCE(version, 'NULL'),
            description,
            type,
            script,
            COALESCE(checksum::TEXT, 'NULL'),
            installed_on,
            execution_time,
            success
        ),
        E'\n'
        ORDER BY installed_rank DESC
    )
    INTO migration_history
    FROM flyway_schema_history
    ORDER BY installed_rank DESC
    LIMIT 20;

    RAISE EXCEPTION E'FLYWAY MIGRATION HISTORY (last 20):\n%', migration_history;
END $$;

-- Grant permissions to cumulus_user (the API user)
GRANT USAGE ON SCHEMA cumulus TO cumulus_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON cumulus.user_region TO cumulus_user;
GRANT SELECT ON cumulus.v_user_region TO cumulus_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA cumulus TO cumulus_user;

-- Also ensure cumulus_user can access other required tables for the view
GRANT SELECT ON cumulus.download TO cumulus_user;

-- Log what we did
DO $$
BEGIN
    RAISE NOTICE 'Granted user_region permissions to cumulus_user';
END
$$;