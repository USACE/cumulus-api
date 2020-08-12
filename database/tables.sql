-- extensions
CREATE extension IF NOT EXISTS "uuid-ossp";


-- drop tables if they already exist
drop table if exists 
    public.office,
    public.basin,
    public.parameter,
    public.unit,
    public.product,
    public.productfile,
    public.key,
    public.acquirable,
    public.acquisition,
    public.acquirable_acquisition,
    public.download,
    public.download_product,
    public.download_status_id
	CASCADE;


-- office
CREATE TABLE IF NOT EXISTS public.office (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    symbol VARCHAR(120) UNIQUE NOT NULL,
    name VARCHAR(120) UNIQUE NOT NULL
);

-- basin
CREATE TABLE IF NOT EXISTS public.basin (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    slug VARCHAR(240) UNIQUE NOT NULL,
    name VARCHAR(120) NOT NULL,
    geometry geometry,
    x_min INTEGER NOT NULL,
    y_min INTEGER NOT NULL,
    x_max INTEGER NOT NULL,
    y_max INTEGER NOT NULL,
    office_id UUID NOT NULL REFERENCES office (id)
);

-- parameter
CREATE TABLE IF NOT EXISTS public.parameter (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(120) UNIQUE NOT NULL
);

-- unit
CREATE TABLE IF NOT EXISTS public.unit (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(120) UNIQUE NOT NULL
);

-- product
CREATE TABLE IF NOT EXISTS public.product (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(120) NOT NULL,
    temporal_duration INTEGER NOT NULL,
    temporal_resolution INTEGER NOT NULL,
    dss_fpart VARCHAR(40),
    is_realtime BOOLEAN,
    parameter_id UUID NOT NULL REFERENCES parameter (id),
    unit_id UUID NOT NULL REFERENCES unit (id)
);

-- productfile
CREATE TABLE IF NOT EXISTS public.productfile (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    datetime TIMESTAMPTZ NOT NULL,
    file VARCHAR(1200) NOT NULL,
    product_id UUID REFERENCES product (id)
);

-- token
CREATE TABLE IF NOT EXISTS public.key (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    key_id VARCHAR(240) UNIQUE NOT NULL,
    issued TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    hash VARCHAR(240) NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE
);

-- acquirable
CREATE TABLE IF NOT EXISTS public.acquirable (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(120) NOT NULL,
    schedule VARCHAR(120)
);

-- acquisition
CREATE TABLE IF NOT EXISTS public.acquisition (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    datetime TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- acquirable_acquisition
CREATE TABLE IF NOT EXISTS public.acquirable_acquisition (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    acquisition_id UUID REFERENCES acquisition (id),
    acquirable_id UUID REFERENCES acquirable (id)
);

-- download_status_id
CREATE TABLE IF NOT EXISTS public.download_status (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(120) NOT NULL
);

-- download
CREATE TABLE IF NOT EXISTS public.download (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    datetime_start TIMESTAMPTZ NOT NULL,
    datetime_end TIMESTAMPTZ NOT NULL,
    geom geometry,
    progress INTEGER NOT NULL,
    status_id UUID REFERENCES download_status(id),
    file VARCHAR(240),
    processing_start TIMESTAMPTZ NOT NULL DEFAULT now(),
    processing_end TIMESTAMPTZ
);

-- download_product
CREATE TABLE IF NOT EXISTS public.download_product (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES product(id),
    download_id UUID REFERENCES download(id)
);

------------------------
-- SEED DATA FOR DOMAINS
------------------------

-- unit
INSERT INTO unit (id, name) VALUES
('4bcfac2e-1a08-4484-bf7d-3cb937dc950b','DEGC-D'),
('8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6','DEG C'),
('e245d39f-3209-4e58-bfb7-4eae94b3f8dd','MM'),
('855ee63c-d623-40d5-a551-3655ce2d7b47','K');

-- parameter
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

-- download_status_id
INSERT INTO download_status (id, name) VALUES
('94727878-7a50-41f8-99eb-a80eb82f737a', 'INITIATED'),
('3914f0bd-2290-42b1-bc24-41479b3a846f', 'SUCCESS'),
('a553101e-8c51-4ddd-ac2e-b011ed54389b', 'FAILED');
