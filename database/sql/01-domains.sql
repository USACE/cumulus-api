-- extensions
CREATE extension IF NOT EXISTS "uuid-ossp";


-- drop tables if they already exist
drop table if exists
    public.config,
    public.unit,
    public.parameter
    CASCADE;

-- config (application config variables)
CREATE TABLE IF NOT EXISTS public.config (
    config_name VARCHAR UNIQUE NOT NULL,
    config_value VARCHAR NOT NULL
);

INSERT INTO config (config_name, config_value) VALUES
('write_to_bucket', 'cwbi-data-develop');


-- unit
CREATE TABLE IF NOT EXISTS public.unit (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(120) UNIQUE NOT NULL,
    abbreviation VARCHAR(120) UNIQUE NOT NULL
);
INSERT INTO unit (id, name, abbreviation) VALUES
    ('4bcfac2e-1a08-4484-bf7d-3cb937dc950b','DEGC-D','DEGC-D'),
    ('8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6','DEG C','DEG-C'),
    ('e245d39f-3209-4e58-bfb7-4eae94b3f8dd','MM','MM'),
    ('855ee63c-d623-40d5-a551-3655ce2d7b47','K','K');


-- parameter
CREATE TABLE IF NOT EXISTS public.parameter (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(120) UNIQUE NOT NULL
);
INSERT INTO parameter (id, name) VALUES
    ('2b3f8cf3-d3f5-440b-b7e7-0c8090eda80f','COLD CONTENT'),
    ('5fab39b9-90ba-482a-8156-d863ad7c45ad','AIRTEMP'),
    ('683a55b9-4a94-46b5-9f47-26e66f3037a8','SWE'),
    ('b93b92c7-8b0b-48c3-a0cf-7124f15197dd','LIQUID WATER'),
    ('ca7b6a70-b662-4f5c-86c7-5588d1cd6cc1','COLD CONTENT ATI'),
    ('cfa90543-235c-4266-98c2-26dbc332cd87','SNOW DEPTH'),
    ('d0517a82-21dd-46a2-bd6d-393ebd504480','MELTRATE ATI'),
    ('eb82d661-afe6-436a-b0df-2ab0b478a1af','PRECIP'),
    ('d3f49557-2aef-4dc2-a2dd-01b353b301a4','SNOW MELT'),
    ('ccc8c81a-ddb0-4738-857b-f0ef69aa1dc0','SNOWTEMP');