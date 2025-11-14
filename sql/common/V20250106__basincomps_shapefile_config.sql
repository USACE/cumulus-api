-- BasinComps Shapefile-Based Configuration
-- Replaces basin-level config with shapefile-level config

-- Drop old basin-based configuration
DROP VIEW IF EXISTS v_basincomps_basin_config;
DROP TABLE IF EXISTS basincomps_basin_config;

-- Shapefile configuration: maps each shapefile to its product list
CREATE TABLE IF NOT EXISTS basincomps_shapefile_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_name VARCHAR(100) NOT NULL,         -- Unique name for this configuration
    description TEXT,                          -- Optional description
    shapefile_path TEXT NOT NULL,              -- Path to shapefile (in container or S3)
    product_ids UUID[] NOT NULL,               -- Products to process for this shapefile
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(config_name)
);

CREATE INDEX IF NOT EXISTS idx_basincomps_shapefile_config_name ON basincomps_shapefile_config(config_name);
CREATE INDEX IF NOT EXISTS idx_basincomps_shapefile_config_enabled ON basincomps_shapefile_config(enabled);

-- Note: Views are created in R__11_views_basincomps.sql (repeatable migration)
-- This allows them to reference v_product which is created in R__04_views_products.sql

COMMENT ON TABLE basincomps_shapefile_config IS 'Configuration for each shapefile and its associated products';
COMMENT ON COLUMN basincomps_shapefile_config.config_name IS 'Unique identifier for this shapefile configuration (e.g., "russian-river", "sacramento")';
COMMENT ON COLUMN basincomps_shapefile_config.shapefile_path IS 'Path to the shapefile containing basin polygons';
COMMENT ON COLUMN basincomps_shapefile_config.product_ids IS 'Array of product UUIDs to process for all basins in this shapefile';
