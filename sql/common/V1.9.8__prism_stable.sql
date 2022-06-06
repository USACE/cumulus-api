INSERT INTO acquirable (id, name, slug) VALUES   
    ('c1b5f8a5-f357-4c1a-9ec1-854db35c71d9', 'prism_ppt_stable', 'prism-ppt-stable'),
    ('3952d221-502f-4937-b860-db8d4b3df435', 'prism_tmax_stable', 'prism-tmax-stable'),
    ('8a20fb67-7c47-46be-b61d-73be8584300f', 'prism_tmin_stable', 'prism-tmin-stable');


INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_fpart,parameter_id,description,unit_id,deleted,suite_id) VALUES
    ('981aa7ef-3066-404d-8c73-32d347b9d8c9','prism-tmax-stable','TMAX',86400,86400,'PRISM-STABLE','5fab39b9-90ba-482a-8156-d863ad7c45ad','Daily maximum temperature [averaged over all days in the month]','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6',false,'9252e4e6-18fa-4a33-a3b6-6f99b5e56f13'),
    ('61fcae9d-cd50-4c00-998b-0a69fc4a2203','prism-tmin-stable','TMIN',86400,86400,'PRISM-STABLE','5fab39b9-90ba-482a-8156-d863ad7c45ad','Daily minimum temperature [averaged over all days in the month]','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6',false,'9252e4e6-18fa-4a33-a3b6-6f99b5e56f13'),
    ('b86e81b0-a860-46b1-bbc8-23b02234a4d2','prism-ppt-stable','PPT',86400,86400,'PRISM-STABLE','eb82d661-afe6-436a-b0df-2ab0b478a1af','Daily total precipitation (rain+melted snow)','e245d39f-3209-4e58-bfb7-4eae94b3f8dd',false,'9252e4e6-18fa-4a33-a3b6-6f99b5e56f13');
