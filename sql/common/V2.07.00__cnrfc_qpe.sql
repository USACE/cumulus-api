-- add acquirable
INSERT INTO acquirable (id, name, slug) VALUES
    ('34a89c35-090d-46e8-964a-c621403301b9', 'cnrfc-qpe-06h', 'cnrfc-qpe-06h');

-- add product suite
INSERT INTO suite (id, name, slug, description) VALUES
    ('469552d5-51f8-40d3-b1f4-658af894c3e8', 'California Nevada River Forecast Center (CNRFC)', 'cnrfc', 'CNRFC Description');

-- add product
INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_fpart,parameter_id,description,unit_id,deleted,suite_id) VALUES
    ('eac3976f-6503-442d-bf20-1a2ffe555162','cnrfc-qpe','QPE',21600,21600,'CNRFC-QPE','eb82d661-afe6-436a-b0df-2ab0b478a1af','CNRFC Quantitative Precipitation Estimate (QPE)','e245d39f-3209-4e58-bfb7-4eae94b3f8dd',false,'469552d5-51f8-40d3-b1f4-658af894c3e8');

-- product_tags
INSERT INTO product_tags (product_id, tag_id) VALUES
    ('eac3976f-6503-442d-bf20-1a2ffe555162','726039da-2f21-4393-a15c-5f6e7ea41b1f');
