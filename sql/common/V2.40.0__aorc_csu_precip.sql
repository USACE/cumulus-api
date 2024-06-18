-- add acquirable
INSERT INTO acquirable (id, name, slug) VALUES
    ('de840786-5c2d-4d94-baf9-5f9195f42463', 'aorc-csu-precip', 'aorc-csu-precip');


INSERT INTO suite (id, name, slug, description) VALUES
    ('b87f898e-184d-47e2-a550-b25c33ebc4e0', 'Analysis Of Record for Calibration (AORC)', 'aorc', 'The Analysis Of Record for Calibration (AORC) is a gridded record of near-surface weather conditions covering the continental United States and Alaska and their hydrologically contributing areas.');

-- add product
INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_fpart,parameter_id,description,unit_id,deleted,suite_id,acceptable_timedelta,dss_datatype_id) VALUES
    ('12180440-9ab6-4c6c-b790-4cea558e85a7', 'aorc-csu-precip', '', 3600, 3600, 'AORC', 'eb82d661-afe6-436a-b0df-2ab0b478a1af', 'The Analysis Of Record for Calibration (AORC) is a gridded record of near-surface weather conditions covering the continental United States and Alaska and their hydrologically contributing areas. This product contains AORC 800m hourly precipitation data archived by Colorado State University (CSU).', 'e245d39f-3209-4e58-bfb7-4eae94b3f8dd', false, 'b87f898e-184d-47e2-a550-b25c33ebc4e0', NULL, '392f8984-2e4e-47ea-ae24-dad81d87f662');
