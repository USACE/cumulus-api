-- Create table for storing user-defined regions
-- Users can save frequently used custom regions for reuse in downloads and searches

CREATE TABLE IF NOT EXISTS user_region (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sub UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    geojson TEXT NOT NULL, -- Store the GeoJSON as text
    geometry geometry(Geometry, 4326) GENERATED ALWAYS AS (ST_GeomFromGeoJSON(geojson)) STORED, -- Auto-generate PostGIS geometry
    bbox FLOAT[] GENERATED ALWAYS AS (
        ARRAY[
            ST_XMin(ST_GeomFromGeoJSON(geojson))::FLOAT,
            ST_YMin(ST_GeomFromGeoJSON(geojson))::FLOAT,
            ST_XMax(ST_GeomFromGeoJSON(geojson))::FLOAT,
            ST_YMax(ST_GeomFromGeoJSON(geojson))::FLOAT
        ]
    ) STORED, -- Auto-calculate bounding box in WGS84
    area_sqkm FLOAT GENERATED ALWAYS AS (
        ST_Area(ST_Transform(ST_GeomFromGeoJSON(geojson), 5070)) / 1000000.0
    ) STORED, -- Auto-calculate area in square kilometers
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_public BOOLEAN DEFAULT FALSE, -- Allow sharing regions with other users
    tags TEXT[], -- Optional tags for categorization
    CONSTRAINT unique_user_region_name UNIQUE(sub, name) -- Each user must have unique region names
);

-- Index for fast lookups
CREATE INDEX idx_user_region_sub ON user_region(sub);
CREATE INDEX idx_user_region_geometry ON user_region USING GIST(geometry);
CREATE INDEX idx_user_region_public ON user_region(is_public) WHERE is_public = TRUE;
CREATE INDEX idx_user_region_tags ON user_region USING GIN(tags);

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

COMMENT ON TABLE user_region IS 'Stores user-defined geographic regions for reuse in downloads and searches';
COMMENT ON COLUMN user_region.sub IS 'User who created the region';
COMMENT ON COLUMN user_region.name IS 'User-friendly name for the region';
COMMENT ON COLUMN user_region.geojson IS 'GeoJSON representation of the region';
COMMENT ON COLUMN user_region.geometry IS 'PostGIS geometry (auto-generated from GeoJSON)';
COMMENT ON COLUMN user_region.bbox IS 'Bounding box [minX, minY, maxX, maxY] in WGS84';
COMMENT ON COLUMN user_region.area_sqkm IS 'Area of the region in square kilometers';
COMMENT ON COLUMN user_region.is_public IS 'If true, region is visible to all users';
COMMENT ON COLUMN user_region.tags IS 'Optional tags for organizing regions';