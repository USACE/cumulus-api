
-------------------------
-- FUNCTIONS AND TRIGGERS
-- User Regions
-------------------------

-- Function to validate GeoJSON before saving
CREATE OR REPLACE FUNCTION validate_user_region_geojson()
RETURNS TRIGGER AS $$
BEGIN
    -- Validate the GeoJSON
    IF NEW.geojson IS NULL OR NEW.geojson = '' THEN
        RAISE EXCEPTION 'GeoJSON cannot be empty';
    END IF;

    -- Try to parse it as geometry
    BEGIN
        PERFORM ST_GeomFromGeoJSON(NEW.geojson);
    EXCEPTION
        WHEN OTHERS THEN
            RAISE EXCEPTION 'Invalid GeoJSON format: %', SQLERRM;
    END;

    -- Validate the geometry
    IF NOT ST_IsValid(ST_GeomFromGeoJSON(NEW.geojson)) THEN
        RAISE EXCEPTION 'Invalid geometry in GeoJSON';
    END IF;

    -- Update the updated_at timestamp
    NEW.updated_at = NOW();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add trigger for validation
CREATE TRIGGER validate_user_region_before_insert_update
    BEFORE INSERT OR UPDATE ON user_region
    FOR EACH ROW
    EXECUTE FUNCTION validate_user_region_geojson();
