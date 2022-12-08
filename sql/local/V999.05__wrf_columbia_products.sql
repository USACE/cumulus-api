-- insert acquirable
INSERT INTO acquirable(id, name, slug) VALUES
    ('e8ce6e5c-1eb8-459e-9da7-5e9e43006c47', 'wrf-columbia', 'wrf-columbia')
ON CONFLICT (id) DO NOTHING;

-- insert new products
INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_datatype_id, dss_fpart,parameter_id,description,unit_id,deleted,suite_id) VALUES
    ('5b6ea634-7a59-41be-ae56-a38a5e7e1632','wrf-columbia-precipah','',3600,3600, '392f8984-2e4e-47ea-ae24-dad81d87f662', 'WRF-COLUMBIA','eb82d661-afe6-436a-b0df-2ab0b478a1af','Precipitation','e245d39f-3209-4e58-bfb7-4eae94b3f8dd',false,'894205d5-cc55-4071-946b-d4027004cb40'),
    ('97e1e3a5-6791-411a-b4b4-37ec16398e3b','wrf-columbia-t2','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-COLUMBIA','37281336-ac37-4824-b83f-bcbc37a64daf','Air temperature at 2 meter','0c8dcd1f-93db-4e64-be1d-47b3462deb2a',false,'894205d5-cc55-4071-946b-d4027004cb40'),
    ('ff23d2b2-9481-4ba5-9df0-0512a2da774c','wrf-columbia-groundt','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-COLUMBIA','ca11ed97-02b9-4a44-9280-70c08bc0d5f9','Surface skin temperature (GROUND_T)','0c8dcd1f-93db-4e64-be1d-47b3462deb2a',false,'894205d5-cc55-4071-946b-d4027004cb40'),
    ('4c30740c-7729-485f-932f-94938cd90770','wrf-columbia-u10','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-COLUMBIA','2d03d408-dd0e-4b6e-8944-e453c63222a7','U (horizontal component towards east) wind velocity at 10 m (U10_____)','d5e7b710-f759-4eef-a0eb-d3148d81c43c',false,'894205d5-cc55-4071-946b-d4027004cb40'),
    ('665d13d1-f894-4297-9442-8351950ccddb','wrf-columbia-v10','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-COLUMBIA','c563cb29-b7b9-4f73-b1c3-a87d931ff5e0','V (horizontal component towards north) wind velocity at 10 m (V10_____)','d5e7b710-f759-4eef-a0eb-d3148d81c43c',false,'894205d5-cc55-4071-946b-d4027004cb40'),
    ('dd64968b-fb65-448d-a418-3bfa44ed51f8','wrf-columbia-pstarcrs','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-COLUMBIA','8328aa49-2c7d-454c-b7e7-d9b2ffeba728','Surface pressure (PSTARCRS)','c32186a9-28c8-4fda-84cf-a107d4fd40b4',false,'894205d5-cc55-4071-946b-d4027004cb40'),
    ('5fb03bff-126b-4cc9-8162-cb054c757487','wrf-columbia-vaporps','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-COLUMBIA','90cf9fe0-ded9-45a8-abc6-78aa25f3fde3','Vapor pressure (VAPOR_PS)','c32186a9-28c8-4fda-84cf-a107d4fd40b4',false,'894205d5-cc55-4071-946b-d4027004cb40'),
    ('962ec366-e022-45d4-9528-f995b53c29e1','wrf-columbia-dewpntt','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-COLUMBIA','1997ea14-9908-46e5-8d59-0ec7b1b7fc5d','Dew point temperature (DEWPNT_T)','0c8dcd1f-93db-4e64-be1d-47b3462deb2a',false,'894205d5-cc55-4071-946b-d4027004cb40'),
    ('fa6d9ae6-f307-4330-8e5c-24e10b137c22','wrf-columbia-rh','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-COLUMBIA','c2c25499-1bc0-4c92-b429-446eaaf37768','Relative humidity (RH______)','5dd42877-0967-432e-9d84-a0b7239b4647',false,'894205d5-cc55-4071-946b-d4027004cb40'),
    ('6f138d28-b398-455a-8465-46e2ce1fc302','wrf-columbia-swdown','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-COLUMBIA','14dc8407-f63a-4237-8251-5ef1746c3d89','Shortwave radiation (SWDOWN__)','880d70f4-d17a-44ba-8f1c-8ff58a87ef89',false,'894205d5-cc55-4071-946b-d4027004cb40'),
    ('2e3786cd-ea7e-46c4-8156-bc86abe7104b','wrf-columbia-lwdown','',0,3600, 'b1433fa7-645f-4e3c-b560-29cba59e80c6', 'WRF-COLUMBIA','6f3efef3-6d6c-4378-94e3-0d7be7321707','Longwave radiation (LWDOWN__)','880d70f4-d17a-44ba-8f1c-8ff58a87ef89',false,'894205d5-cc55-4071-946b-d4027004cb40')
ON CONFLICT (id) DO NOTHING;

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
    ('2e3786cd-ea7e-46c4-8156-bc86abe7104b','17308048-d207-43dd-b346-c9836073e911')
ON CONFLICT ON CONSTRAINT unique_tag_product DO NOTHING;
