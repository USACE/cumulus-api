-- NBM products with QPF are one hour for forecasts hours 1-264
-- NBM products with QTF are one hour for the first 36 hours,
-- 3 hour to forecast hour 192, and 6 hour to 264

-- inserting qpf and qtf acquirable
INSERT INTO acquirable (id, name, slug) VALUES
    ('6ddb2d43-f880-49a2-b0f4-3ddc7ed9e3d8', 'nbm-co-qpf-06h', 'nbm-co-qpf-06h'),
    ('1e755c6f-1410-4e72-af5d-53237d248681', 'nbm-co-qtf-01h', 'nbm-co-qtf-01h'),
    ('e1119f5a-e57e-4513-ab01-daa875b910a2', 'nbm-co-qtf-03h', 'nbm-co-qtf-03h'),
    ('8f7330cd-dfc4-4085-bb5b-ecaa9e597c39', 'nbm-co-qtf-06h', 'nbm-co-qtf-06h');

-- insert products
INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_fpart,parameter_id,description,unit_id,deleted,suite_id,acceptable_timedelta,dss_datatype_id) VALUES
    ('2d82ef5e-cf5d-430a-94ee-61af29a796e3','nbm-co-qpf-06h','QPF',21600,21600,'NBM-QPF06','eb82d661-afe6-436a-b0df-2ab0b478a1af','National Blend of Models precipitation forecast, 6 hour','e245d39f-3209-4e58-bfb7-4eae94b3f8dd',false,'c9b39f25-51e5-49cd-9b5a-77c575bebc3b','7 hour','392f8984-2e4e-47ea-ae24-dad81d87f662'),
    ('f43cb3b8-221a-4ff0-aaa6-5937e54323b6','nbm-co-qtf-03h','QTF',0,10800,'NBM','5fab39b9-90ba-482a-8156-d863ad7c45ad','National Blend of Models air temperature forecast, 3 hour','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6',false,'c9b39f25-51e5-49cd-9b5a-77c575bebc3b','4 hour','b1433fa7-645f-4e3c-b560-29cba59e80c6'),
    ('7e5c7acf-7d2b-4d02-a582-7ddf9b2e3700','nbm-co-qtf-06h','QTF',0,21600,'NBM','5fab39b9-90ba-482a-8156-d863ad7c45ad','National Blend of Models air temperature forecast, 6 hour','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6',false,'c9b39f25-51e5-49cd-9b5a-77c575bebc3b','7 hour','b1433fa7-645f-4e3c-b560-29cba59e80c6');

-- rename fpart for NBM QPF 01Hr
UPDATE product
    SET dss_fpart = 'NBM-QPF01'
    WHERE id = '5317d1c4-c6db-40c2-b527-72f7603be8a0';

-- rename fpart for NBM QTF
UPDATE product
    SET dss_fpart = 'NBM-QTF'
    WHERE id = 'd0c1d6f4-cf5d-4332-a17e-dd1757c99c94';
