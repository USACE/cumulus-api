-- insert new acquirable
INSERT INTO acquirable (id, name, slug) VALUES   
    ('234ab142-a434-471b-a8c6-7b41ee341ac4', 'wrf-columbia', 'wrf-columbia');

-- insert new products
INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_datatype_id, dss_fpart,parameter_id,description,unit_id,deleted,suite_id) VALUES
    ('ff23d2b2-9481-4ba5-9df0-0512a2da774c','wrf-columbia-groundt','Surface Skin Temperature [F]',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'Surface Skin Temperature','256e12c8-93d4-4a79-b3ac-6259426a189a','Surface skin temperature (GROUND_T)','0c8dcd1f-93db-4e64-be1d-47b3462deb2a',false,'894205d5-cc55-4071-946b-d4027004cb40'),
    ('4c30740c-7729-485f-932f-94938cd90770','wrf-columbia-u10','U wind at 10m [m/s]',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'U wind at 10m','a4cbef84-fd47-415a-910c-d143dcb20ba4','U (horizontal component towards east) wind velocity at 10 m (U10_____)','d5e7b710-f759-4eef-a0eb-d3148d81c43c',false,'894205d5-cc55-4071-946b-d4027004cb40'),
    ('665d13d1-f894-4297-9442-8351950ccddb','wrf-columbia-v10','V wind at 10m [m/s]',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'V wind at 10m','a4cbef84-fd47-415a-910c-d143dcb20ba4','V (horizontal component towards north) wind velocity at 10 m (V10_____)','d5e7b710-f759-4eef-a0eb-d3148d81c43c',false,'894205d5-cc55-4071-946b-d4027004cb40'),
    ('dd64968b-fb65-448d-a418-3bfa44ed51f8','wrf-columbia-pstarcrs','Surface Pressure [hPa]',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'Surface','f1d2fee8-ac86-499f-83be-b15bcde43d76','Surface pressure (PSTARCRS)','c32186a9-28c8-4fda-84cf-a107d4fd40b4',false,'894205d5-cc55-4071-946b-d4027004cb40'),
    ('5fb03bff-126b-4cc9-8162-cb054c757487','wrf-columbia-vaporps','Vapor Pressure [hPa]',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'Vapor','f1d2fee8-ac86-499f-83be-b15bcde43d76','Vapor pressure (VAPOR_PS)','c32186a9-28c8-4fda-84cf-a107d4fd40b4',false,'894205d5-cc55-4071-946b-d4027004cb40'),
    ('962ec366-e022-45d4-9528-f995b53c29e1','wrf-columbia-dewpntt','Dew Point Temperature [F]',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'Dew point','256e12c8-93d4-4a79-b3ac-6259426a189a','Dew point temperature (DEWPNT_T)','0c8dcd1f-93db-4e64-be1d-47b3462deb2a',false,'894205d5-cc55-4071-946b-d4027004cb40'),
    ('fa6d9ae6-f307-4330-8e5c-24e10b137c22','wrf-columbia-rh','Relative Humidity [%]',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'Relative Humidity','8dd6420d-e624-45c0-90ed-b5ec3756d2f1','Relative humidity (RH______)','5dd42877-0967-432e-9d84-a0b7239b4647',false,'894205d5-cc55-4071-946b-d4027004cb40'),
    ('6f138d28-b398-455a-8465-46e2ce1fc302','wrf-columbia-swdown','Shorwave Radiation [W/m2]',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'Shortwave','7586a687-7f31-4fa0-8447-eb31d199a05a','Shortwave radiation (SWDOWN__)','880d70f4-d17a-44ba-8f1c-8ff58a87ef89',false,'894205d5-cc55-4071-946b-d4027004cb40'),
    ('2e3786cd-ea7e-46c4-8156-bc86abe7104b','wrf-columbia-lwdown','Longwave Radiation [W/m2]',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'Longwave','7586a687-7f31-4fa0-8447-eb31d199a05a','Longwave radiation (LWDOWN__)','880d70f4-d17a-44ba-8f1c-8ff58a87ef89',false,'894205d5-cc55-4071-946b-d4027004cb40');

-- update Columbia Precip
UPDATE product SET
    slug = 'wrf-columbia-precipah',
    label = 'Precipitation [mm/hr]',
    description = 'Precipitation (PRECIPAH)',
    dss_fpart = 'Precipitation (PRECIPAH)'
    WHERE slug = 'wrf-columbia-precip';

-- update Columbia Temperature at 2m
UPDATE product SET
    slug = 'wrf-columbia-t2',
    label = 'Temperature at 2m [F]',
    description = 'Air temperature at 2m (t2)',
    dss_fpart = 'Air Temp at 2m'
    WHERE slug = 'wrf-columbia-airtemp';

-- WRF product tags
INSERT INTO product_tags (product_id, tag_id) VALUES
    ('ff23d2b2-9481-4ba5-9df0-0512a2da774c','17308048-d207-43dd-b346-c9836073e911'),
    ('4c30740c-7729-485f-932f-94938cd90770','17308048-d207-43dd-b346-c9836073e911'),
    ('665d13d1-f894-4297-9442-8351950ccddb','17308048-d207-43dd-b346-c9836073e911'),
    ('dd64968b-fb65-448d-a418-3bfa44ed51f8','17308048-d207-43dd-b346-c9836073e911'),
    ('5fb03bff-126b-4cc9-8162-cb054c757487','17308048-d207-43dd-b346-c9836073e911'),
    ('962ec366-e022-45d4-9528-f995b53c29e1','17308048-d207-43dd-b346-c9836073e911'),
    ('fa6d9ae6-f307-4330-8e5c-24e10b137c22','17308048-d207-43dd-b346-c9836073e911'),
    ('6f138d28-b398-455a-8465-46e2ce1fc302','17308048-d207-43dd-b346-c9836073e911'),
    ('2e3786cd-ea7e-46c4-8156-bc86abe7104b','17308048-d207-43dd-b346-c9836073e911');