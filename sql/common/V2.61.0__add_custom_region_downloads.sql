-- Add support for custom GeoJSON regions in downloads
-- This allows users to download data clipped to their exact area of interest
-- instead of being limited to predefined watershed boundaries

-- Add column to store custom clip region as GeoJSON
ALTER TABLE download ADD COLUMN IF NOT EXISTS clip_geojson TEXT;

-- Add column to store the clip region name (optional)
ALTER TABLE download ADD COLUMN IF NOT EXISTS clip_region_name VARCHAR(255);

-- Note: The v_download view is updated in the repeatable migration R__05_views_downloads.sql
-- to include the new clip_geojson and clip_region_name columns