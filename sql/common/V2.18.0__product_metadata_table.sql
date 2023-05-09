-- create new table to contain specific product metadata
-- table data to be displayed in UI per product
-- product_metadat
CREATE TABLE IF NOT EXISTS product_metadata (
    product_id UUID,
    description VARCHAR,
    driver_short_name VARCHAR,
    driver_long_name VARCHAR,
    crs_proj4 VARCHAR,
    time_zone VARCHAR DEFAULT 'GMT',
    acquisition_source VARCHAR DEFAULT 'https://',
    source_reference VARCHAR DEFAULT 'https://',
    raster_xsize INT,
    raster_ysize INT,
    notes TEXT DEFAULT ''
);

INSERT INTO product_metadata (product_id, description, driver_short_name, driver_long_name, crs_proj4, acquisition_source, source_reference, raster_xsize, raster_ysize, notes) VALUES
    ('bfa3366a-49ef-4a08-99e7-2cb2e24624c9', 'ABRFC Precipitation', 'netCDF', 'Network Common Data Format', '+proj=stere +lat_0=90 +lat_ts=90 +lon_0=-105 +x_0=0 +y_0=0 +R=6371200 +units=m +no_defs', 'https://', 'https://', 2345, 1597, 'notes');
