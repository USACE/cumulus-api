-- add acquirable
INSERT INTO acquirable (id, 
                        name, 
                        slug) 
                        VALUES ('80f33047-6234-4949-9c2f-eec6bfcf7b0f', 
                        'aprfc-qtf-01h', 
                        'aprfc-qtf-01h');


-- add product
INSERT INTO product (id,
                    slug,
                    "label",
                    temporal_duration,
                    temporal_resolution,
                    dss_fpart,
                    parameter_id,
                    description,
                    unit_id,
                    deleted,
                    suite_id,
                    acceptable_timedelta,
                    dss_datatype_id) 
                    VALUES ('7d613d9e-148e-476f-9b65-cacb8ab6e7f1',
                    'aprfc-qtf-01h',
                    'QTF',
                    0,
                    3600,
                    'APRFC-QTF',
                    '5fab39b9-90ba-482a-8156-d863ad7c45ad',
                    'Alaska-Pacific River Forecast Center Forecasted 1 Hour Air Temperature at Surface',
                    '8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6',
                    false,
                    'a3a20fc7-537a-4670-afdd-af248d9566d1',
                    '26 hour',
                    'b1433fa7-645f-4e3c-b560-29cba59e80c6');