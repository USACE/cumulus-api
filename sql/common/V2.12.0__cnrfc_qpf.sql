-- add acquirable
INSERT INTO acquirable (id, name, slug) VALUES
    ('c22785cd-400e-4664-aef8-426734825c2c', 'cnrfc-qpf-06h', 'cnrfc-qpf-06h');

-- add product
INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_fpart,parameter_id,description,unit_id,deleted,suite_id) VALUES
	 ('f6f25a98-1de8-4546-b5d6-e2e0ff761db3','cnrfc-qpf','QPF',21600,21600,'CNRFC-QPF','eb82d661-afe6-436a-b0df-2ab0b478a1af','CNRFC Quantitative Precipitation Forecast (QPF)','e245d39f-3209-4e58-bfb7-4eae94b3f8dd',false,'469552d5-51f8-40d3-b1f4-658af894c3e8');

-- product_tags
INSERT INTO product_tags (product_id, tag_id) VALUES
    ('f6f25a98-1de8-4546-b5d6-e2e0ff761db3','726039da-2f21-4393-a15c-5f6e7ea41b1f'),
    ('f6f25a98-1de8-4546-b5d6-e2e0ff761db3','cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a');