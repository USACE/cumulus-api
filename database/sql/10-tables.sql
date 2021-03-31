-- extensions
CREATE extension IF NOT EXISTS "uuid-ossp";


-- drop tables if they already exist
drop table if exists
    public.area_group_product_statistics_enabled,
    public.area,
    public.area_group,
    public.office,
    public.parameter,
    public.unit,
    public.product,
    public.productfile,
    public.acquirable,
    public.acquisition,
    public.acquirable_acquisition,
    public.download,
    public.download_product,
    public.download_status,
	public.profile_token,
	public.profile,
    public.watershed,
    public.profile_watersheds
	CASCADE;


-- office
CREATE TABLE IF NOT EXISTS public.office (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    symbol VARCHAR(120) UNIQUE NOT NULL,
    name VARCHAR(120) UNIQUE NOT NULL
);

-- profile
CREATE TABLE IF NOT EXISTS public.profile (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    edipi BIGINT UNIQUE NOT NULL,
    email VARCHAR(240) UNIQUE NOT NULL
);

-- profile_token
CREATE TABLE IF NOT EXISTS public.profile_token (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    token_id VARCHAR NOT NULL,
    profile_id UUID NOT NULL REFERENCES profile(id),
    issued TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    hash VARCHAR(240) NOT NULL
);

-- watershed
CREATE TABLE IF NOT EXISTS public.watershed (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    slug VARCHAR UNIQUE NOT NULL,
    name VARCHAR,
    geometry geometry,
    office_id UUID REFERENCES office(id)
);

-- profile_watersheds
CREATE TABLE IF NOT EXISTS public.profile_watersheds (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    watershed_id UUID NOT NULL REFERENCES watershed(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES profile(id) ON DELETE CASCADE,
    CONSTRAINT profile_unique_watershed UNIQUE(watershed_id, profile_id)

);

-- area_group
CREATE TABLE IF NOT EXISTS public.area_group (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    watershed_id UUID NOT NULL REFERENCES watershed(id) ON DELETE CASCADE,
    slug VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    CONSTRAINT watershed_unique_slug UNIQUE(watershed_id, slug),
    CONSTRAINT watershed_unique_name UNIQUE(watershed_id, name)
);

-- area
CREATE TABLE IF NOT EXISTS public.area (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    slug VARCHAR UNIQUE NOT NULL,
    name VARCHAR UNIQUE NOT NULL,
    geometry geometry NOT NULL,
    area_group_id UUID NOT NULL REFERENCES area_group(id) ON DELETE CASCADE,
    CONSTRAINT area_group_unique_slug UNIQUE(area_group_id, slug),
    CONSTRAINT area_group_unique_name UNIQUE(area_group_id, name)
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

CREATE TABLE IF NOT EXISTS public.product_group (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR NOT NULL
);

-- acquirable
CREATE TABLE IF NOT EXISTS public.acquirable (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(120) NOT NULL,
    slug VARCHAR(120) UNIQUE NOT NULL
);

-- acquirablefile
CREATE TABLE IF NOT EXISTS public.acquirablefile (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(120) NOT NULL,
    slug VARCHAR(120) UNIQUE NOT NULL,
    create_date TIMESTAMPTZ NOT NULL,
    process_date TIMESTAMPTZ,
    acquirable_id UUID not null REFERENCES acquirable (id)
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

-- product
CREATE TABLE IF NOT EXISTS public.product (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    slug VARCHAR(120) UNIQUE NOT NULL,
    group_id UUID REFERENCES product_group(id),
    name VARCHAR(120) NOT NULL,
    temporal_duration INTEGER NOT NULL,
    temporal_resolution INTEGER NOT NULL,
    dss_fpart VARCHAR(40),
    is_realtime BOOLEAN NOT NULL,
    is_forecast BOOLEAN NOT NULL,
    parameter_id UUID NOT NULL REFERENCES parameter (id),
    description TEXT NOT NULL DEFAULT '',
    unit_id UUID NOT NULL REFERENCES unit (id)
);

-- productfile
CREATE TABLE IF NOT EXISTS public.productfile (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    datetime TIMESTAMPTZ NOT NULL,
    file VARCHAR(1200) NOT NULL,
    product_id UUID REFERENCES product (id),
    version TIMESTAMPTZ NOT NULL DEFAULT '1111-11-11T11:11:11.11Z',
    acquirablefile_id UUID REFERENCES acquirablefile (id),
    CONSTRAINT unique_product_version_datetime UNIQUE(product_id, version, datetime)
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
    progress INTEGER NOT NULL DEFAULT 0,
    status_id UUID REFERENCES download_status(id),
    watershed_id UUID REFERENCES watershed(id),
    file VARCHAR(240),
    processing_start TIMESTAMPTZ NOT NULL DEFAULT now(),
    processing_end TIMESTAMPTZ,
    profile_id UUID REFERENCES profile(id)
);

-- download_product
CREATE TABLE IF NOT EXISTS public.download_product (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES product(id),
    download_id UUID REFERENCES download(id)
);

-- area_group_product_statistics_enabled
CREATE TABLE IF NOT EXISTS public.area_group_product_statistics_enabled (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    area_group_id UUID NOT NULL REFERENCES area_group(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES product(id) ON DELETE CASCADE,
    CONSTRAINT unique_area_group_product UNIQUE(area_group_id, product_id)
);

-- Function; Notify New Record in Table
CREATE OR REPLACE FUNCTION public.notify_new ()
  returns trigger
  language plpgsql
AS $$
declare
    channel text := 'cumulus_new';
begin
	PERFORM (
		WITH payload as (
			SELECT TG_TABLE_NAME AS table, NEW.id AS id
		)
		SELECT pg_notify(channel, row_to_json(payload)::text)
		FROM payload
	);
	RETURN NULL;
end;
$$;

-- Trigger; NOTIFY NEW DOWNLOAD ON INSERT
CREATE TRIGGER notify_new_download
AFTER INSERT ON public.download
FOR EACH ROW
EXECUTE PROCEDURE public.notify_new();

-- -- Trigger; NOTIFY NEW PRODUCTFILE ON INSERT
CREATE TRIGGER notify_new_productfile
AFTER INSERT
ON public.productfile
FOR EACH ROW
EXECUTE PROCEDURE public.notify_new();

------------------------
-- SEED DATA FOR DOMAINS
------------------------

-- product_group
INSERT INTO product_group (id, name) VALUES
    ('726039da-2f21-4393-a15c-5f6e7ea41b1f', 'PRECIPITATION'),
    ('d9613031-7cf0-4722-923e-e5c3675a163b', 'TEMPERATURE'),
    ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05', 'SNOW');

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

