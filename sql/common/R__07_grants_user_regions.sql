-- Repeatable migration to ensure user_region permissions are always correct
-- This runs every time migrations are applied to ensure permissions are set

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