-- add acquirable

INSERT INTO acquirable (id, name, slug) VALUES
    ('7f8b2d6a-1f3e-11ee-be56-0242ac120002', 'aprfc-qte-01h', 'aprfc-qte-01h');
--    (' dc0bcd4a-1f3e-11ee-be56-0242ac120002', 'aprfc-qtf-01h', 'aprfc-qtf-01h');

--INSERT INTO suite (id, name, slug, description) VALUES
--    ('a3a20fc7-537a-4670-afdd-af248d9566d1', 'Alaska-Pacific River Forecast Center (APRFC)', 'aprfc', 'APRFC Description');

-- add product
INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_fpart,parameter_id,description,unit_id,deleted,suite_id,acceptable_timedelta,dss_datatype_id) VALUES
    ('b1d47c2e-1f3e-11ee-be56-0242ac120002','aprfc-qte-01h','QTE',0,3600,'APRFC-QTE','5fab39b9-90ba-482a-8156-d863ad7c45ad','Alaska-Pacific River Forecast Center 1 Hour Air temperature at 2 meter','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6',false,'a3a20fc7-537a-4670-afdd-af248d9566d1','30 hour','b1433fa7-645f-4e3c-b560-29cba59e80c6');
--    ('c6f89a3c-1f3e-11ee-be56-0242ac120002','aprfc-qfe-01h','QTF',0,3600,'APRFC-QTF','5fab39b9-90ba-482a-8156-d863ad7c45ad','Alaska-Pacific River Forecast Center 1 Hour Forecasted Air temperature at 2 meter','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6',false,'a3a20fc7-537a-4670-afdd-af248d9566d1','30 hour','b1433fa7-645f-4e3c-b560-29cba59e80c6'),