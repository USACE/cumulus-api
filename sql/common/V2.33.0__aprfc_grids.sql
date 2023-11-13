-- add acquirable
INSERT INTO acquirable (id, name, slug) VALUES
    ('1f67d822-7cbc-11ee-b962-0242ac120002', 'aprfc-qpe-06h', 'aprfc-qpe-06h'),
    ('a64cb16f-01a8-45c0-a069-9afda805d3a7', 'aprfc-qpf-06h', 'aprfc-qpf-06h');

INSERT INTO suite (id, name, slug, description) VALUES
    ('a3a20fc7-537a-4670-afdd-af248d9566d1', 'Alaska-Pacific River Forecast Center (APRFC)', 'aprfc', 'APRFC Description');

-- add product
INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_fpart,parameter_id,description,unit_id,deleted,suite_id,acceptable_timedelta,dss_datatype_id) VALUES
    ('03463100-7e53-11ee-b962-0242ac120002','aprfc-qpe-06h','QPE',21600,21600,'APRFC-QPE','eb82d661-afe6-436a-b0df-2ab0b478a1af','Alaska-Pacific River Forecast Center 6-Hour QPE','c5eba078-61d1-46a0-b2e6-b7d41ec9c924',false,'a3a20fc7-537a-4670-afdd-af248d9566d1','30 hour','392f8984-2e4e-47ea-ae24-dad81d87f662'),
    ('18e9d048-7e53-11ee-b962-0242ac120002','aprfc-qpf-06h','QPF',21600,21600,'APRFC-QPF','eb82d661-afe6-436a-b0df-2ab0b478a1af','Alaska-Pacific River Forecast Center 6-Hour QPF','c5eba078-61d1-46a0-b2e6-b7d41ec9c924',false,'a3a20fc7-537a-4670-afdd-af248d9566d1','30 hour','392f8984-2e4e-47ea-ae24-dad81d87f662');