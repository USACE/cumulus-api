-- acquirable
INSERT INTO acquirable (id, name, slug) VALUES
    ('6c879d18-2eca-4b35-9fab-2b5f78262fa6', 'ncrfc-rtmat-01h', 'ncrfc-rtmat-01h'),
    ('28d16afe-2834-4d2c-9df2-fdf2c40e510f', 'ncrfc-fmat-01h', 'ncrfc-fmat-01h'),
    ('a483aa42-4388-4289-a41e-6b78998066a7', 'ncep-mrms-v12-msqpe01h-p2-carib', 'ncep-mrms-v12-msqpe01h-p2-carib'),
    ('e5dfeef2-f070-49dc-8f3c-1c9230000f96', 'ncep-mrms-v12-msqpe01h-p1-carib', 'ncep-mrms-v12-msqpe01h-p1-carib'),
    ('1860dfa9-0d2c-4b75-84ed-516792d940ee', 'ncep-mrms-v12-msqpe01h-p2-alaska', 'ncep-mrms-v12-msqpe01h-p2-alaska'),
    ('cf75d07d-d527-4be0-b066-0bfa86565ab5', 'ncep-mrms-v12-msqpe01h-p1-alaska', 'ncep-mrms-v12-msqpe01h-p1-alaska'),
    ('5fc5d74a-6684-4ffb-886a-663848ba22d9', 'marfc-rtmat-01h', 'marfc-rtmat-01h'),
    ('e2228d8c-204a-4c7e-849b-a9a7e5c13eca', 'marfc-nbmt-03h', 'marfc-nbmt-03h'),
    ('af651a3b-03ad-424d-8cf7-9ca7230309ed', 'marfc-nbmt-01h', 'marfc-nbmt-01h'),
    ('7093dd22-2fa4-4172-b67d-5abc586e5eb6', 'marfc-fmat-06h', 'marfc-fmat-06h');

-- suite
INSERT INTO suite (id, name, slug, description) VALUES
    ('839c527c-cd05-4d04-a533-bbf5c0b2a3b0', 'North Central River Forecast Center (NCRFC)', 'ncrfc', 'NCRFC Description'),
    ('cc901b66-99fd-4671-9b68-a0bb8fc4223f', 'Middle Atlantic River Forecast Center (MARFC)', 'marfc', 'MARFC Description');

-- product
INSERT INTO product (id, slug, label, temporal_duration, temporal_resolution, dss_fpart, parameter_id, unit_id, description, suite_id) VALUES
    ('0de4d4a8-2a18-4564-a14d-fb426c2046a8','ncrfc-mpe-01h','NCRFC QPE 01 Hr',3600,3600,'NCRFC QPE 01 HR','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd','North Central River Forecast Center 01 hour QPE','839c527c-cd05-4d04-a533-bbf5c0b2a3b0'),
    ('8e8adafa-9240-47df-857c-e2cec4b3dc62','ncrfc-rtmat-01h','NCRFC RTMS Observed Surface Temperature',3600,3600,'NCRFC OBS SURFACE TEMP','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6','North Central River Forecast Center 01 hour observed surface temperatures','839c527c-cd05-4d04-a533-bbf5c0b2a3b0'),
    ('71644147-5910-4e65-9195-43c37fc6ddc6','ncrfc-fmat-01h','NCRFC Mesoscale Surface Temperature',3600,3600,'NCRFC MESO SURFACE TEMP','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6','North Central River Forecast Center 01 hour forecasted surface temperatures','839c527c-cd05-4d04-a533-bbf5c0b2a3b0'),
    ('78c193b4-00ea-46d6-8a97-60dcbd0d64f5','ncep-mrms-v12-msqpe01h-p2-carib','MRMS QPE Pass 2',3600,3600,'NCEP MRMS v12 QPE PASS 2','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd','Southeast River Forecast Center 01 hour Multisensor Pass 2 QPE','e9730ce6-2ff2-4dbe-ab77-47237a0fd598'),
    ('bb45d8e4-830e-4d96-98ab-3dd04370192a','ncep-mrms-v12-msqpe01h-p1-carib','MRMS QPE Pass 1',3600,3600,'NCEP MRMS v12 QPE PASS 1','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd','Southeast River Forecast Center 01 hour Multisensor Pass 1 QPE','e9730ce6-2ff2-4dbe-ab77-47237a0fd598'),
    ('c88d6cad-21de-4fd9-a680-64abf3d6a923','ncep-mrms-v12-msqpe01h-p2-alaska','MRMS QPE Pass 2',3600,3600,'NCEP MRMS v12 QPE PASS 2','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd','Alaska Pacific River Forecast Center 01 hour Multisensor Pass 2 QPE','e9730ce6-2ff2-4dbe-ab77-47237a0fd598'),
    ('70d9be00-ad3e-4509-9511-730e57a32987','ncep-mrms-v12-msqpe01h-p1-alaska','MRMS QPE Pass 1',3600,3600,'NCEP MRMS v12 QPE PASS 1','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd','Alaska Pacific River Forecast Center 01 hour Multisensor Pass 1 QPE','e9730ce6-2ff2-4dbe-ab77-47237a0fd598'),
    ('c3976ec6-cbe0-4f68-a6d5-03beb9514041','marfc-rtmat-01h','MARFC',3600,3600,'MARFC QTE 01 HR','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6','Middle Atlanctic River Forecast Center 01 hour Realtime Mesoscale Analysis QTE','cc901b66-99fd-4671-9b68-a0bb8fc4223f'),
    ('4b556067-9610-42fc-a71d-0fa0fcbd8ea1','marfc-nbmt-03h','MARFC',10800,10800,'MARFC QTF 03 HR','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6','Middle Atlanctic River Forecast Center 03 hour National Blend of Models QTF','cc901b66-99fd-4671-9b68-a0bb8fc4223f'),
    ('90a3d16b-dde2-43a8-aced-16f6aeaaf70a','marfc-nbmt-01h','MARFC',3600,3600,'MARFC QTF 01 HR','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6','Middle Atlanctic River Forecast Center 01 hour National Blend of Models QTF','cc901b66-99fd-4671-9b68-a0bb8fc4223f'),
    ('8b5672d2-2cf1-4ccf-8785-8a9d9302b3a8','marfc-fmat-06h','MARFC',21600,21600,'MARFC QTF 06 HR','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6','Middle Atlanctic River Forecast Center 06 hour QTF','cc901b66-99fd-4671-9b68-a0bb8fc4223f');
