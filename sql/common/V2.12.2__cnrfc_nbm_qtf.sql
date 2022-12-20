-- NBM QTF

-- add acquirable
INSERT INTO acquirable (id, name, slug) VALUES
    ('0b1772a1-5567-4189-b892-750797ce02a1', 'cnrfc-nbm-qtf-01h', 'cnrfc-nbm-qtf-01h');

-- add product
-- note: units are DEG F
INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_fpart,parameter_id,description,unit_id,deleted,suite_id,acceptable_timedelta,dss_datatype_id) VALUES
	 ('bec1f1ad-9b43-4ecb-a2f8-f9f9b2d3368c','cnrfc-nbm-qtf-01h','NBM QTF',0,3600,'CNRFC-NBM-QTF','5fab39b9-90ba-482a-8156-d863ad7c45ad','CNRFC National Blend of Models (NBM) Quantitative Temperature Forecast (QTF)','0c8dcd1f-93db-4e64-be1d-47b3462deb2a',false,'469552d5-51f8-40d3-b1f4-658af894c3e8','7 hour','b1433fa7-645f-4e3c-b560-29cba59e80c6');