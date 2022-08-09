INSERT INTO acquirable (id, name, slug) VALUES   
    ('1011b702-9cb7-4b86-9638-ccbf2c19086f', 'ncep-stage4-mosaic-06h', 'ncep-stage4-mosaic-06h'),
    ('758958c4-0938-428e-8221-621bd07e9a34', 'ncep-stage4-mosaic-24h', 'ncep-stage4-mosaic-24h');

INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_fpart,parameter_id,description,unit_id,deleted,suite_id) VALUES
    ('c49940e8-768d-4525-9094-4de87bc25447','ncep-stage4-mosaic-06h','STAGE4 MOSAIC QPE',21600,21600,'NCEP-STAGE4-06h','eb82d661-afe6-436a-b0df-2ab0b478a1af','Precipitation estimates by the 12 River Forecast Centers (RFCs) in CONUS','e245d39f-3209-4e58-bfb7-4eae94b3f8dd',false,'96d0250c-bf16-447f-8ccc-b15134c1ab99'),
    ('3cb28e6d-6fbd-45d8-9a32-2c4f4aa2cae2','ncep-stage4-mosaic-24h','STAGE4 MOSAIC QPE',86400,86400,'NCEP-STAGE4-24h','eb82d661-afe6-436a-b0df-2ab0b478a1af','Precipitation estimates by the 12 River Forecast Centers (RFCs) in CONUS','e245d39f-3209-4e58-bfb7-4eae94b3f8dd',false,'96d0250c-bf16-447f-8ccc-b15134c1ab99');

UPDATE product SET acceptable_timedelta = '7 hour' WHERE slug = 'ncep-stage4-mosaic-06h';
UPDATE product SET acceptable_timedelta = '48 hour' WHERE slug = 'ncep-stage4-mosaic-24h';
