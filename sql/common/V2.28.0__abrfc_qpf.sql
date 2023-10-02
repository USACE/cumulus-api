-- add acquirable
INSERT INTO acquirable (id, name, slug) VALUES
    ('b1a4754c-5971-11ee-8c99-0242ac120002', 'abrfc-qpf-06h', 'abrfc-qpf-06h');

-- add product
INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_fpart,parameter_id,description,unit_id,deleted,suite_id,acceptable_timedelta,dss_datatype_id) VALUES
    ('e4a6aca8-5971-11ee-8c99-0242ac120002','abrfc-qpf-06h','QPF',21600,21600,'ABRFC-QPF','eb82d661-afe6-436a-b0df-2ab0b478a1af','Arkansas-Red Basin River Forecast Center 6-Hour QPF','c5eba078-61d1-46a0-b2e6-b7d41ec9c924',false,'40d3e055-c812-47a2-a6eb-b9943a236496','7 hour','392f8984-2e4e-47ea-ae24-dad81d87f662');