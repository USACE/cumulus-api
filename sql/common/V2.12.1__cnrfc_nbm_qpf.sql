-- NBM QPF

-- add acquirable
INSERT INTO acquirable (id, name, slug) VALUES
    ('40cfce36-cfad-4a10-8b2d-eb8862378ca5', 'cnrfc-nbm-qpf-06h', 'cnrfc-nbm-qpf-06h');

-- add product
-- note: units are INCHES
INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_fpart,parameter_id,description,unit_id,deleted,suite_id,acceptable_timedelta,dss_datatype_id) VALUES
	 ('5e19db39-ba57-4a65-ba5b-dc213a1c1b7f','cnrfc-nbm-qpf-06h','NBM QPF',21600,21600,'CNRFC-NBM-QPF','eb82d661-afe6-436a-b0df-2ab0b478a1af','CNRFC National Blend of Models (NBM) Quantitative Precipitation Forecast (QPF)','c5eba078-61d1-46a0-b2e6-b7d41ec9c924',false,'469552d5-51f8-40d3-b1f4-658af894c3e8','7 hour','392f8984-2e4e-47ea-ae24-dad81d87f662');