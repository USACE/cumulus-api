-- add suite
INSERT INTO suite (id, name, slug, description) VALUES
    ('b1df7e88-9db6-4383-97bc-494beaf1965e', 'Northwest River Forecast Center (NWRFC)', 'nwrfc', 'NWRFC Description');

---------------------
-- add nwrfc-qpe-06h
---------------------

-- add acquirable
INSERT INTO acquirable (id, name, slug) VALUES
    ('faeb67de-0b9c-496c-88d4-b1513056b149', 'nwrfc-qpe-06h', 'nwrfc-qpe-06h');

-- add product
INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_fpart,parameter_id,description,unit_id,deleted,suite_id,acceptable_timedelta,dss_datatype_id) VALUES
    ('5bfec3ee-3f11-4142-b959-b76c28ca5170','nwrfc-qpe-06h','QPE',21600,21600,'NWRFC-QPE','eb82d661-afe6-436a-b0df-2ab0b478a1af','NWRFC Quantitative Precipitation Estimate (QPE)','e245d39f-3209-4e58-bfb7-4eae94b3f8dd',false,'b1df7e88-9db6-4383-97bc-494beaf1965e','24 hour','392f8984-2e4e-47ea-ae24-dad81d87f662');

    
---------------------
-- add nwrfc-qpf-06h
---------------------

-- add acquirable
INSERT INTO acquirable (id, name, slug) VALUES
    ('ad7b4457-f46f-453c-9370-29773d28c423', 'nwrfc-qpf-06h', 'nwrfc-qpf-06h');

-- add product
INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_fpart,parameter_id,description,unit_id,deleted,suite_id,acceptable_timedelta,dss_datatype_id) VALUES
    ('a10d5f10-9074-4afc-925d-1271e469226e','nwrfc-qpf-06h','QPF',21600,21600,'NWRFC-QPF','eb82d661-afe6-436a-b0df-2ab0b478a1af','NWRFC Quantitative Precipitation Forecast (QPF)','e245d39f-3209-4e58-bfb7-4eae94b3f8dd',false,'b1df7e88-9db6-4383-97bc-494beaf1965e','24 hour','392f8984-2e4e-47ea-ae24-dad81d87f662');

---------------------
-- add nwrfc-qte-06h
---------------------

-- add acquirable
INSERT INTO acquirable (id, name, slug) VALUES
    ('09c9ff0c-c49d-47fd-b4cd-9696480dc0da', 'nwrfc-qte-06h', 'nwrfc-qte-06h');

-- add product
INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_fpart,parameter_id,description,unit_id,deleted,suite_id,acceptable_timedelta,dss_datatype_id) VALUES
	 ('d60307f1-55d4-4ca8-86d5-516b399427c5','nwrfc-qte-06h','QTE',0,21600,'NWRFC-QTE','5fab39b9-90ba-482a-8156-d863ad7c45ad','NWRFC Quantitative Temperature Estimate (QTE)','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6',false,'b1df7e88-9db6-4383-97bc-494beaf1965e','24 hour','b1433fa7-645f-4e3c-b560-29cba59e80c6');


---------------------
-- add nwrfc-qtf-06h
---------------------

-- add acquirable
INSERT INTO acquirable (id, name, slug) VALUES
    ('31aff91f-53ba-4352-86d1-233bac999f43', 'nwrfc-qtf-06h', 'nwrfc-qtf-06h');

-- add product
INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_fpart,parameter_id,description,unit_id,deleted,suite_id,acceptable_timedelta,dss_datatype_id) VALUES
	 ('630ea9a7-9ef3-47ff-9e99-77d23af78ceb','nwrfc-qtf-06h','QTF',0,21600,'NWRFC-QTF','5fab39b9-90ba-482a-8156-d863ad7c45ad','NWRFC Quantitative Temperature Forecast (QTF)','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6',false,'b1df7e88-9db6-4383-97bc-494beaf1965e','24 hour','b1433fa7-645f-4e3c-b560-29cba59e80c6');
