INSERT INTO acquirable (id, name, slug) VALUES   
    ('f7500b0e-5227-44fb-bcf1-746be7574cf0', 'abrfc-qpe-01h', 'abrfc-qpe-01h');

INSERT INTO suite (id, name, slug, description) VALUES
    ('40d3e055-c812-47a2-a6eb-b9943a236496', 'Arkansas-Red Basin River Forecast Center (ABRFC)', 'abrfc', 'The ABRFC provides technical support to the National Weather Services efforts to provide river and flood forecasts and warnings for protection of life and property and to provide basic hydrologic forecast information for the nations economic and environmental well-being. The ABRFC area of responsibility includes the drainage area of the Arkansas River above Pine Bluff Arkansas and the drainage area of the Red River above Fulton Arkansas. This comprises over 208,000 square miles and includes portions of seven states.');

INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_fpart,parameter_id,description,unit_id,deleted,suite_id) VALUES
    ('bfa3366a-49ef-4a08-99e7-2cb2e24624c9','abrfc-qpe-01h','ABRFC QPE',3600,3600,'ABRFC-QPE','eb82d661-afe6-436a-b0df-2ab0b478a1af','Arkansas-Red Basin River Forecast Center 1-Hour QPE','e245d39f-3209-4e58-bfb7-4eae94b3f8dd',false,'40d3e055-c812-47a2-a6eb-b9943a236496');

UPDATE product SET acceptable_timedelta = '2 hour' WHERE slug = 'abrfc-qpe-01h';
