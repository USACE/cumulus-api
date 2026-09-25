-- Add AORC (Analysis of Record for Calibration) suite
INSERT INTO suite (id, name, slug, description) VALUES
    ('a3c7e1f0-8d24-4b6a-9f12-3e5a7c9b1d04', 'NOAA Analysis of Record for Calibration (AORC)', 'noaa-aorc', 'NOAA Office of Water Prediction Analysis of Record for Calibration - gridded hourly meteorological forcing data at 1km resolution');

---------------------
-- add aorc-precip-01h
---------------------

-- add acquirable
INSERT INTO acquirable (id, name, slug) VALUES
    ('b4d8f2a1-9e35-4c7b-a023-4f6b8d0c2e15', 'aorc-precip-01h', 'aorc-precip-01h');

-- add product
-- note: units are MM; AORC APCP_surface is precipitation accumulation in kg/m^2 (equivalent to mm)
-- temporal_resolution = 3600 (hourly); temporal_duration = 3600 (1 hour accumulation)
INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_fpart,parameter_id,description,unit_id,deleted,suite_id,acceptable_timedelta,dss_datatype_id) VALUES
    ('c5e9a3b2-0f46-4d8c-b134-5a7c9e1d3f26','aorc-precip-01h','PRECIP',3600,3600,'AORC-PRECIP','eb82d661-afe6-436a-b0df-2ab0b478a1af','NOAA AORC Hourly Precipitation (APCP_surface) - Analysis of Record for Calibration v1.1 at 1km resolution','e245d39f-3209-4e58-bfb7-4eae94b3f8dd',false,'a3c7e1f0-8d24-4b6a-9f12-3e5a7c9b1d04',NULL,'392f8984-2e4e-47ea-ae24-dad81d87f662');

-- add precipitation tag
INSERT INTO product_tags (product_id, tag_id) VALUES
    ('c5e9a3b2-0f46-4d8c-b134-5a7c9e1d3f26', '726039da-2f21-4393-a15c-5f6e7ea41b1f');

-- add archive tag
INSERT INTO product_tags (product_id, tag_id) VALUES
    ('c5e9a3b2-0f46-4d8c-b134-5a7c9e1d3f26', '17308048-d207-43dd-b346-c9836073e911');
