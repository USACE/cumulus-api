-- insert new acquirable
INSERT INTO acquirable (id, name, slug) VALUES   
    ('52dbf840-276d-4c19-b2fb-b4d8539abf5f', 'wrf-bc', 'wrf-bc');

-- insert a new suit
INSERT INTO suite (id, name, slug, description) VALUES
    ('a274d10d-f01f-4b82-860c-2ac75286d61d', 'Weather Research and Forecasting Model (WRF) British Columbia', 'wrf-british-columbia', '');

-- insert new products
INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_datatype_id, dss_fpart,parameter_id,description,unit_id,deleted,suite_id) VALUES
    ('ece6c741-1116-453e-bad6-f2416cffbb5b','wrf-bc-precipah','',3600,3600, '392f8984-2e4e-47ea-ae24-dad81d87f662', 'WRF-BRITISH-COLUMBIA','eb82d661-afe6-436a-b0df-2ab0b478a1af','Precipitation (PRECIPAH)','e245d39f-3209-4e58-bfb7-4eae94b3f8dd',false,'a274d10d-f01f-4b82-860c-2ac75286d61d'),
    ('60ae0bf5-3b96-4e2c-8d9a-989470e885c3','wrf-bc-t2','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-BRITISH-COLUMBIA','37281336-ac37-4824-b83f-bcbc37a64daf','Air Temperature at 2m (T2)','0c8dcd1f-93db-4e64-be1d-47b3462deb2a',false,'a274d10d-f01f-4b82-860c-2ac75286d61d'),
    ('4378048a-5231-406c-b8fd-2dd8fce8bbb2','wrf-bc-groundt','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-BRITISH-COLUMBIA','ca11ed97-02b9-4a44-9280-70c08bc0d5f9','Surface skin temperature (GROUND_T)','0c8dcd1f-93db-4e64-be1d-47b3462deb2a',false,'a274d10d-f01f-4b82-860c-2ac75286d61d'),
    ('40a5f450-5d56-4302-b479-3b878586b051','wrf-bc-u10','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-BRITISH-COLUMBIA','2d03d408-dd0e-4b6e-8944-e453c63222a7','U (horizontal component towards east) wind velocity at 10 m (U10_____)','d5e7b710-f759-4eef-a0eb-d3148d81c43c',false,'a274d10d-f01f-4b82-860c-2ac75286d61d'),
    ('06fb2b38-984d-40bc-a368-7052c78c5075','wrf-bc-v10','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-BRITISH-COLUMBIA','c563cb29-b7b9-4f73-b1c3-a87d931ff5e0','V (horizontal component towards north) wind velocity at 10 m (V10_____)','d5e7b710-f759-4eef-a0eb-d3148d81c43c',false,'a274d10d-f01f-4b82-860c-2ac75286d61d'),
    ('e5f65f9a-12f7-4e07-a15a-8a11f43143d4','wrf-bc-pstarcrs','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-BRITISH-COLUMBIA','8328aa49-2c7d-454c-b7e7-d9b2ffeba728','Surface pressure (PSTARCRS)','c32186a9-28c8-4fda-84cf-a107d4fd40b4',false,'a274d10d-f01f-4b82-860c-2ac75286d61d'),
    ('40cf8865-a125-4b9d-ac46-fc48a75142bb','wrf-bc-vaporps','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-BRITISH-COLUMBIA','90cf9fe0-ded9-45a8-abc6-78aa25f3fde3','Vapor pressure (VAPOR_PS)','c32186a9-28c8-4fda-84cf-a107d4fd40b4',false,'a274d10d-f01f-4b82-860c-2ac75286d61d'),
    ('85cceeb1-467f-4775-a453-8a78b3e3e045','wrf-bc-dewpntt','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-BRITISH-COLUMBIA','1997ea14-9908-46e5-8d59-0ec7b1b7fc5d','Dew point temperature (DEWPNT_T)','0c8dcd1f-93db-4e64-be1d-47b3462deb2a',false,'a274d10d-f01f-4b82-860c-2ac75286d61d'),
    ('754b5bcc-ebf7-41c0-b675-b80ad37fb954','wrf-bc-rh','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-BRITISH-COLUMBIA','c2c25499-1bc0-4c92-b429-446eaaf37768','Relative humidity (RH______)','5dd42877-0967-432e-9d84-a0b7239b4647',false,'a274d10d-f01f-4b82-860c-2ac75286d61d'),
    ('35a79907-7a04-4e25-a2d3-400edb442eac','wrf-bc-swdown','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-BRITISH-COLUMBIA','14dc8407-f63a-4237-8251-5ef1746c3d89','Shortwave radiation (SWDOWN__)','880d70f4-d17a-44ba-8f1c-8ff58a87ef89',false,'a274d10d-f01f-4b82-860c-2ac75286d61d'),
    ('13b83148-c00b-4206-afa8-59f4356be7f9','wrf-bc-lwdown','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-BRITISH-COLUMBIA','6f3efef3-6d6c-4378-94e3-0d7be7321707','Longwave radiation (LWDOWN__)','880d70f4-d17a-44ba-8f1c-8ff58a87ef89',false,'a274d10d-f01f-4b82-860c-2ac75286d61d');

-- WRF product tags
INSERT INTO product_tags (product_id, tag_id) VALUES
    ('ece6c741-1116-453e-bad6-f2416cffbb5b','17308048-d207-43dd-b346-c9836073e911'),
    ('60ae0bf5-3b96-4e2c-8d9a-989470e885c3','17308048-d207-43dd-b346-c9836073e911'),
    ('4378048a-5231-406c-b8fd-2dd8fce8bbb2','17308048-d207-43dd-b346-c9836073e911'),
    ('40a5f450-5d56-4302-b479-3b878586b051','17308048-d207-43dd-b346-c9836073e911'),
    ('06fb2b38-984d-40bc-a368-7052c78c5075','17308048-d207-43dd-b346-c9836073e911'),
    ('e5f65f9a-12f7-4e07-a15a-8a11f43143d4','17308048-d207-43dd-b346-c9836073e911'),
    ('40cf8865-a125-4b9d-ac46-fc48a75142bb','17308048-d207-43dd-b346-c9836073e911'),
    ('85cceeb1-467f-4775-a453-8a78b3e3e045','17308048-d207-43dd-b346-c9836073e911'),
    ('754b5bcc-ebf7-41c0-b675-b80ad37fb954','17308048-d207-43dd-b346-c9836073e911'),
    ('35a79907-7a04-4e25-a2d3-400edb442eac','17308048-d207-43dd-b346-c9836073e911'),
    ('13b83148-c00b-4206-afa8-59f4356be7f9','17308048-d207-43dd-b346-c9836073e911');
