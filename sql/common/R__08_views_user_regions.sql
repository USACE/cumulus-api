
-------------------------
-- VIEWS
-- User Regions
-------------------------

-- View for user regions with additional computed fields
CREATE OR REPLACE VIEW v_user_region AS
SELECT
    ur.id,
    ur.sub,
    ur.name,
    ur.description,
    ur.geojson,
    ur.bbox,
    ur.area_sqkm,
    ur.created_at,
    ur.updated_at,
    ur.is_public,
    ur.tags,
    -- Count how many times this region has been used in downloads
    (SELECT COUNT(*)
     FROM download d
     WHERE d.sub = ur.sub
       AND d.clip_region_name = ur.name) AS usage_count
FROM user_region ur;

-- Grant permissions (commented out if roles don't exist yet)
-- GRANT SELECT ON user_region, v_user_region TO cumulus_reader;
-- GRANT INSERT, UPDATE, DELETE ON user_region TO cumulus_writer;
