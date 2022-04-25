-- Change the following products to have a temporal_duration of 0
-- ndfd-conus-airtemp-03h
-- ndfd-conus-airtemp-06h
-- nbm-co-airtemp
-- marfc-rtmat-01h
-- marfc-fmat-06h
-- marfc-nbmt-01h
-- ncrfc-rtmat-01h
-- wrf-columbia-airtemp

UPDATE product set temporal_duration = 0 
where id in 
(
    'dde59007-25ec-4bb4-b5e6-8f0f1fbab853', 
    'f48006a5-ad25-4a9f-9b58-639d75763dd7', 
    'd0c1d6f4-cf5d-4332-a17e-dd1757c99c94',
    'c3976ec6-cbe0-4f68-a6d5-03beb9514041',
    '8b5672d2-2cf1-4ccf-8785-8a9d9302b3a8',
    '90a3d16b-dde2-43a8-aced-16f6aeaaf70a',
    '8e8adafa-9240-47df-857c-e2cec4b3dc62',
    '793e285f-333b-41a3-b4ab-223a7a764668'
);