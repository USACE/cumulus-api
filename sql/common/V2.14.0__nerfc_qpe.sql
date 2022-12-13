-- add suite
INSERT INTO suite (id, name, slug, description) VALUES
    ('c61c6ea1-f276-4663-9d5a-99549e38181a', 'Northeast River Forecast Center (NERFC)', 'nerfc', 'NERFC Description');

---------------------
-- add nwrfc-qpe-06h
---------------------

-- add acquirable
INSERT INTO acquirable (id, name, slug) VALUES
    ('7fdc5c49-ae1d-4492-b8d2-1eb2c3dd5010', 'nerfc-qpe-01h', 'nerfc-qpe-01h');

-- add product
INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_fpart,parameter_id,description,unit_id,deleted,suite_id,acceptable_timedelta,dss_datatype_id) VALUES
    ('8e0be52f-1c48-4884-8168-da9e257f2e21','nerfc-qpe-01h','QPE',3600,3600,'NERFC-QPE','eb82d661-afe6-436a-b0df-2ab0b478a1af','NERFC Quantitative Precipitation Estimate (QPE)','e245d39f-3209-4e58-bfb7-4eae94b3f8dd',false,'c61c6ea1-f276-4663-9d5a-99549e38181a','2 hour','392f8984-2e4e-47ea-ae24-dad81d87f662');
