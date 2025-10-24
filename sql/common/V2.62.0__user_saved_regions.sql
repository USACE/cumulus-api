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

COMMENT ON TABLE user_region IS 'Stores user-defined geographic regions for reuse in downloads and searches';
COMMENT ON COLUMN user_region.sub IS 'User who created the region';
COMMENT ON COLUMN user_region.name IS 'User-friendly name for the region';
COMMENT ON COLUMN user_region.geojson IS 'GeoJSON representation of the region';
COMMENT ON COLUMN user_region.geometry IS 'PostGIS geometry (auto-generated from GeoJSON)';
COMMENT ON COLUMN user_region.bbox IS 'Bounding box [minX, minY, maxX, maxY] in WGS84';
COMMENT ON COLUMN user_region.area_sqkm IS 'Area of the region in square kilometers';
COMMENT ON COLUMN user_region.is_public IS 'If true, region is visible to all users';
COMMENT ON COLUMN user_region.tags IS 'Optional tags for organizing regions';