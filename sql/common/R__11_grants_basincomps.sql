-- Repeatable Migration: Grant permissions on BasinComps tables to cumulus_user
-- Security: Batch run INSERT is protected by stored procedure (SECURITY DEFINER)
-- The scheduler service writes results, API reads them

-- Grant permissions on basincomps_daily_result table (scheduler writes, API reads)
GRANT SELECT, INSERT, UPDATE, DELETE ON cumulus.basincomps_daily_result TO cumulus_user;

-- Grant permissions on basincomps_batch_run table
-- Scheduler needs INSERT to create batch runs, UPDATE to update status
GRANT SELECT, INSERT, UPDATE ON cumulus.basincomps_batch_run TO cumulus_user;

-- Grant permissions on basincomps_rolling_total table (scheduler writes, API reads)
GRANT SELECT, INSERT, UPDATE, DELETE ON cumulus.basincomps_rolling_total TO cumulus_user;

-- Grant permissions on basincomps_shapefile_config table
GRANT SELECT, INSERT, UPDATE, DELETE ON cumulus.basincomps_shapefile_config TO cumulus_user;

-- Grant SELECT on views
GRANT SELECT ON cumulus.v_basincomps_daily_result TO cumulus_user;
GRANT SELECT ON cumulus.v_basincomps_rolling_total TO cumulus_user;
GRANT SELECT ON cumulus.v_basincomps_shapefile_config TO cumulus_user;

-- Grant on v_basincomps_basin_config view (only if it exists)
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_views WHERE schemaname = 'cumulus' AND viewname = 'v_basincomps_basin_config') THEN
        GRANT SELECT ON cumulus.v_basincomps_basin_config TO cumulus_user;
    END IF;
END $$;

-- Grant on basincomps_basin_config table (only if it exists)
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'cumulus' AND tablename = 'basincomps_basin_config') THEN
        GRANT SELECT, INSERT, UPDATE, DELETE ON cumulus.basincomps_basin_config TO cumulus_user;
    END IF;
END $$;

-- Create stored procedure to trigger batch runs (with elevated privileges)
CREATE OR REPLACE FUNCTION cumulus.trigger_basincomps_run()
RETURNS TABLE(batch_id UUID, message TEXT)
LANGUAGE plpgsql
SECURITY DEFINER  -- Runs with permissions of the function owner (postgres)
SET search_path = cumulus, public
AS $$
DECLARE
    v_batch_id UUID;
    v_existing_id UUID;
BEGIN
    -- Check if a batch run already exists for today (same calendar day)
    SELECT id INTO v_existing_id
    FROM cumulus.basincomps_batch_run
    WHERE DATE(run_date) = CURRENT_DATE
      AND status IN ('TRIGGERED', 'RUNNING')
    ORDER BY start_time DESC
    LIMIT 1;

    -- If already exists, return existing batch_id
    IF v_existing_id IS NOT NULL THEN
        RETURN QUERY SELECT v_existing_id, 'Batch run already triggered for today'::TEXT;
        RETURN;
    END IF;

    -- Insert new batch run record
    INSERT INTO cumulus.basincomps_batch_run (run_date, start_time, status)
    VALUES (NOW(), NOW(), 'TRIGGERED')
    RETURNING id INTO v_batch_id;

    -- Return new batch_id
    RETURN QUERY SELECT v_batch_id, 'BasinComps batch run triggered successfully'::TEXT;
END;
$$;

-- Grant EXECUTE permission on the function to cumulus_user
GRANT EXECUTE ON FUNCTION cumulus.trigger_basincomps_run() TO cumulus_user;

-- Add comment
COMMENT ON FUNCTION cumulus.trigger_basincomps_run() IS
'Triggers a BasinComps batch run. Protected by API admin middleware. Uses SECURITY DEFINER to prevent direct table access.';
