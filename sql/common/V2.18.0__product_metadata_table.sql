-- create new table to contain specific product metadata
-- table data to be displayed in UI per product
-- product_metadat
CREATE TABLE IF NOT EXISTS product_metadata (
    product_id UUID NOT NULL REFERENCES product(id) ON DELETE CASCADE,
    driver_short_name VARCHAR DEFAULT 'Unknown',
    driver_long_name VARCHAR DEFAULT 'Unknown',
    coordinate_system VARCHAR DEFAULT 'Unknown',
    time_zone VARCHAR DEFAULT 'GMT',
    source_acquisition VARCHAR DEFAULT 'https://',
    source_reference VARCHAR DEFAULT 'https://',
    raster_xsize INT DEFAULT 0,
    raster_ysize INT DEFAULT 0,
    notes TEXT DEFAULT ''
);

INSERT INTO product_metadata (product_id, driver_short_name, driver_long_name, coordinate_system, source_acquisition, source_reference, raster_xsize, raster_ysize) VALUES
    ('bfa3366a-49ef-4a08-99e7-2cb2e24624c9','netCDF','Network Common Data Format', 'Polar Stereographic', 'https://tgftp.nws.noaa.gov/data/rfc/abrfc/xmrg_qpe/', 'https://', 2345, 1597), --abrfc-qpe-01h
    ('c500f609-428f-4c38-b658-e7dde63de2ea','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://www.cbrfc.noaa.gov/outgoing/usace_la/xmrgMMDDYYYYHHz.grb', 'https://', 9999,9999), --cbrfc-mpe
    ('002125d6-2c90-4c24-9382-10a535d398bb','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/', 'https://', 9999,9999), --hrrr-total-precip
    ('5e13560b-7589-474f-9fd5-bc1cf4163fe4','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --lmrfc-qpe-01h
    ('1c8c130e-0d3c-4ccc-af5b-d2f95379429c','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --lmrfc-qpf-06h
    ('8b5672d2-2cf1-4ccf-8785-8a9d9302b3a8','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --marfc-fmat-06h
    ('90a3d16b-dde2-43a8-aced-16f6aeaaf70a','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --marfc-nbmt-01h
    ('c3976ec6-cbe0-4f68-a6d5-03beb9514041','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --marfc-rtmat-01h
    ('bbfeadbb-1b54-486c-b975-a67d107540f3','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --mbrfc-krf-fct-airtemp-01h
    ('9890d81e-04c5-45cc-b544-e27fde610501','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --mbrfc-krf-qpe-01h
    ('c96f7a1f-e57d-4694-9d09-451cfa949324','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --mbrfc-krf-qpf-06h
    ('a8e3de13-d4fb-4973-a076-c6783c93f332','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --naefs-mean-qpf-06h
    ('60f16079-7495-47ab-aa68-36cd6a17fce0','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --naefs-mean-qtf-06h
    ('d0c1d6f4-cf5d-4332-a17e-dd1757c99c94','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --nbm-co-airtemp
    ('5317d1c4-c6db-40c2-b527-72f7603be8a0','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --nbm-co-qpf
    ('2d82ef5e-cf5d-430a-94ee-61af29a796e3','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --nbm-co-qpf-06h
    ('f43cb3b8-221a-4ff0-aaa6-5937e54323b6','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --nbm-co-qtf-03h
    ('7e5c7acf-7d2b-4d02-a582-7ddf9b2e3700','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --nbm-co-qtf-06h
    ('f1b6ac38-bbc9-48c6-bf78-207005ee74fa','GRIB', 'General Regularly-distributed Information in Binary', 'https://', 'https://', 9999,9999), --ncep-mrms-gaugecorr-qpe-01h
    ('70d9be00-ad3e-4509-9511-730e57a32987','GRIB', 'General Regularly-distributed Information in Binary', 'https://', 'https://', 9999,9999), --ncep-mrms-v12-msqpe01h-p1-alaska
    ('bb45d8e4-830e-4d96-98ab-3dd04370192a','GRIB', 'General Regularly-distributed Information in Binary', 'https://', 'https://', 9999,9999), --ncep-mrms-v12-msqpe01h-p1-carib
    ('c88d6cad-21de-4fd9-a680-64abf3d6a923','GRIB', 'General Regularly-distributed Information in Binary', 'https://', 'https://', 9999,9999), --ncep-mrms-v12-msqpe01h-p2-alaska
    ('78c193b4-00ea-46d6-8a97-60dcbd0d64f5','GRIB', 'General Regularly-distributed Information in Binary', 'https://', 'https://', 9999,9999), --ncep-mrms-v12-msqpe01h-p2-carib
    ('30a6d443-80a5-49cc-beb0-5d3a18a84caa','GRIB', 'General Regularly-distributed Information in Binary', 'https://', 'https://', 9999,9999), --ncep-mrms-v12-multisensor-qpe-01h-pass1
    ('7c7ba37a-efad-499e-9c3a-5354370b8e9e','GRIB', 'General Regularly-distributed Information in Binary', 'https://', 'https://', 9999,9999), --ncep-mrms-v12-multisensor-qpe-01h-pass2
    ('e4fdadc7-5532-4910-9ed7-3c3690305d86','GRIB', 'General Regularly-distributed Information in Binary', 'https://', 'https://', 9999,9999), --ncep-rtma-ru-anl-airtemp
    ('16d4c494-63e6-4d33-b2da-7be065a6776b','GRIB', 'General Regularly-distributed Information in Binary', 'https://', 'https://', 9999,9999), --ncep-stage4-mosaic-01h
    ('c49940e8-768d-4525-9094-4de87bc25447','GRIB', 'General Regularly-distributed Information in Binary', 'https://', 'https://', 9999,9999), --ncep-stage4-mosaic-06h
    ('3cb28e6d-6fbd-45d8-9a32-2c4f4aa2cae2','GRIB', 'General Regularly-distributed Information in Binary', 'https://', 'https://', 9999,9999), --ncep-stage4-mosaic-24h
    ('0de4d4a8-2a18-4564-a14d-fb426c2046a8','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --ncrfc-mpe-01h
    ('8e8adafa-9240-47df-857c-e2cec4b3dc62','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --ncrfc-rtmat-01h
    ('b206a00b-9ed6-42e1-a34d-c67d43828810','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --ndfd-conus-airtemp-01h
    ('dde59007-25ec-4bb4-b5e6-8f0f1fbab853','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --ndfd-conus-airtemp-03h
    ('f48006a5-ad25-4a9f-9b58-639d75763dd7','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --ndfd-conus-airtemp-06h
    ('84a64026-0e5d-49ac-a48a-6a83efa2b77c','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --ndfd-conus-qpf-06h
    ('1ba5498c-d507-4c82-a80b-9b0af952b02f','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --ndgd-leia98-precip
    ('5e6ca7ed-007d-4944-93aa-0a7a6116bdcd','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --ndgd-ltia98-airtemp
    ('8e0be52f-1c48-4884-8168-da9e257f2e21','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --nerfc-qpe-01h
    ('c2f2f0ed-d120-478a-b38f-427e91ab18e2','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --nohrsc-snodas-coldcontent
    ('33407c74-cdc2-4ab2-bd9a-3dff99ea02e4','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --nohrsc-snodas-coldcontent-interpolated
    ('e0baa220-1310-445b-816b-6887465cc94b','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --nohrsc-snodas-snowdepth
    ('2274baae-1dcf-4c4c-92bb-e8a640debee0','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --nohrsc-snodas-snowdepth-interpolated
    ('86526298-78fa-4307-9276-a7c0a0537d15','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --nohrsc-snodas-snowmelt
    ('10011d9c-04a4-454d-88a0-fb7ba0d64d37','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --nohrsc-snodas-snowmelt-interpolated
    ('57da96dc-fc5e-428c-9318-19f095f461eb','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --nohrsc-snodas-snowpack-average-temperature
    ('e97fbc56-ebe2-4d5a-bcd4-4bf3744d8a1b','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --nohrsc-snodas-snowpack-average-temperature-interpolated
    ('757c809c-dda0-412b-9831-cb9bd0f62d1d','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --nohrsc-snodas-swe
    ('75f8cd8c-c0f5-4ee5-9397-4866ad9afcac','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --nohrsc-snodas-swe-corrections
    ('517369a5-7fe3-4b0a-9ef6-10f26f327b26','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --nohrsc-snodas-swe-interpolated
    ('bf73ae80-22fc-43a2-930a-599531470dc6','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --nsidc-ua-snowdepth-v1
    ('87d79a53-5e66-4d31-973c-2adbbe733de2','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --nsidc-ua-swe-v1
    ('5bfec3ee-3f11-4142-b959-b76c28ca5170','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --nwrfc-qpe-06h
    ('a10d5f10-9074-4afc-925d-1271e469226e','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --nwrfc-qpf-06h
    ('d60307f1-55d4-4ca8-86d5-516b399427c5','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --nwrfc-qte-06h
    ('630ea9a7-9ef3-47ff-9e99-77d23af78ceb','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --nwrfc-qtf-06h
    ('64756f41-75e2-40ce-b91a-fda5aeb441fc','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --prism-ppt-early
    ('b86e81b0-a860-46b1-bbc8-23b02234a4d2','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --prism-ppt-stable
    ('6357a677-5e77-4c37-8aeb-3300707ca885','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --prism-tmax-early
    ('981aa7ef-3066-404d-8c73-32d347b9d8c9','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --prism-tmax-stable
    ('62e08d34-ff6b-45c9-8bb9-80df922d0779','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --prism-tmin-early
    ('61fcae9d-cd50-4c00-998b-0a69fc4a2203','driver', 'driver name', 'CRS', 'https://', 'https://', 9999,9999), --prism-tmin-stable
    ('ae11dad4-7065-4963-8771-7f5aa1e94b5d','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --serfc-qpe-01h
    ('a9a74d32-acdb-4fd2-8478-14d7098c50a7','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --serfc-qpf-06h
    ('0ac60940-35c2-4c0d-8a3b-49c20e455ff5','GRIB', 'General Regularly-distributed Information in Binary', 'CRS', 'https://', 'https://', 9999,9999), --wpc-qpf-2p5km
    ('85cceeb1-467f-4775-a453-8a78b3e3e045','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-bc-dewpntt
    ('4378048a-5231-406c-b8fd-2dd8fce8bbb2','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-bc-groundt
    ('13b83148-c00b-4206-afa8-59f4356be7f9','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-bc-lwdown
    ('ece6c741-1116-453e-bad6-f2416cffbb5b','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-bc-precipah
    ('e5f65f9a-12f7-4e07-a15a-8a11f43143d4','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-bc-pstarcrs
    ('754b5bcc-ebf7-41c0-b675-b80ad37fb954','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-bc-rh
    ('35a79907-7a04-4e25-a2d3-400edb442eac','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-bc-swdown
    ('60ae0bf5-3b96-4e2c-8d9a-989470e885c3','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-bc-t2
    ('40a5f450-5d56-4302-b479-3b878586b051','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-bc-u10
    ('06fb2b38-984d-40bc-a368-7052c78c5075','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-bc-v10
    ('40cf8865-a125-4b9d-ac46-fc48a75142bb','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-bc-vaporps
    ('793e285f-333b-41a3-b4ab-223a7a764668','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-columbia-airtemp
    ('962ec366-e022-45d4-9528-f995b53c29e1','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-columbia-dewpntt
    ('ff23d2b2-9481-4ba5-9df0-0512a2da774c','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-columbia-groundt
    ('2e3786cd-ea7e-46c4-8156-bc86abe7104b','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-columbia-lwdown
    ('b50f29f4-547b-4371-9365-60d44eef412e','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-columbia-precip
    ('5b6ea634-7a59-41be-ae56-a38a5e7e1632','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-columbia-precipah
    ('dd64968b-fb65-448d-a418-3bfa44ed51f8','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-columbia-pstarcrs
    ('fa6d9ae6-f307-4330-8e5c-24e10b137c22','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-columbia-rh
    ('6f138d28-b398-455a-8465-46e2ce1fc302','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-columbia-swdown
    ('97e1e3a5-6791-411a-b4b4-37ec16398e3b','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-columbia-t2
    ('4c30740c-7729-485f-932f-94938cd90770','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-columbia-u10
    ('665d13d1-f894-4297-9442-8351950ccddb','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999), --wrf-columbia-v10
    ('5fb03bff-126b-4cc9-8162-cb054c757487','netCDF','Network Common Data Format', 'CRS', 'https://', 'https://', 9999,9999); --wrf-columbia-vaporps;
