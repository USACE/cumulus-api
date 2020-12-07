-- extensions
CREATE extension IF NOT EXISTS "uuid-ossp";


-- drop tables if they already exist
drop table if exists
    public.area_group_product_statistics_enabled,
    public.area,
    public.area_group,
    public.office,
    public.subbasin,
    public.basin,
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
    public.watershed
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

-- watershed
CREATE TABLE IF NOT EXISTS public.watershed (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    slug VARCHAR UNIQUE NOT NULL,
    name VARCHAR,
    geometry geometry
);

-- area_group
CREATE TABLE IF NOT EXISTS public.area_group (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    watershed_id UUID NOT NULL REFERENCES watershed(id) ON DELETE CASCADE,
    slug VARCHAR UNIQUE NOT NULL,
    name VARCHAR UNIQUE NOT NULL
);

-- area
CREATE TABLE IF NOT EXISTS public.area (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    slug VARCHAR UNIQUE NOT NULL,
    name VARCHAR UNIQUE NOT NULL,
    geometry geometry NOT NULL,
    area_group_id UUID NOT NULL REFERENCES area_group(id) ON DELETE CASCADE
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

-- product
CREATE TABLE IF NOT EXISTS public.product (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    group_id UUID REFERENCES product_group(id),
    name VARCHAR(120) NOT NULL,
    temporal_duration INTEGER NOT NULL,
    temporal_resolution INTEGER NOT NULL,
    dss_fpart VARCHAR(40),
    is_realtime BOOLEAN NOT NULL,
    is_forecast BOOLEAN NOT NULL,
    parameter_id UUID NOT NULL REFERENCES parameter (id),
    unit_id UUID NOT NULL REFERENCES unit (id)
);

-- basin_product_statistics_enabled
CREATE TABLE IF NOT EXISTS public.basin_product_statistics_enabled (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    basin_id UUID NOT NULL REFERENCES basin(id),
    product_id UUID NOT NULL REFERENCES product(id),
    CONSTRAINT unique_basin_product UNIQUE(basin_id, product_id)
);

-- productfile
CREATE TABLE IF NOT EXISTS public.productfile (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    datetime TIMESTAMPTZ NOT NULL,
    file VARCHAR(1200) NOT NULL,
    product_id UUID REFERENCES product (id)
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
    progress INTEGER NOT NULL DEFAULT 0,
    status_id UUID REFERENCES download_status(id),
    basin_id UUID REFERENCES basin(id),
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

-- area_group_product_statistics_enabled
CREATE TABLE IF NOT EXISTS public.area_group_product_statistics_enabled (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    area_group_id UUID NOT NULL REFERENCES area_group(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES product(id) ON DELETE CASCADE,
    CONSTRAINT unique_area_group_product UNIQUE(area_group_id, product_id)
);

-- VIEWS
CREATE OR REPLACE VIEW v_download AS (
        SELECT d.id AS id,
            d.datetime_start AS datetime_start,
            d.datetime_end AS datetime_end,
            d.progress AS progress,
            d.file AS file,
            d.processing_start AS processing_start,
            d.processing_end AS processing_end,
            d.status_id AS status_id,
            d.basin_id AS basin_id,
            s.name AS status,
            dp.product_id AS product_id
        FROM download d
            INNER JOIN download_status s ON d.status_id = s.id
            INNER JOIN (
                SELECT array_agg(id) as product_id,
                    download_id
                FROM download_product
                GROUP BY download_id
            ) dp ON d.id = dp.download_id
    );

-- Basins; Projected to EPSG 5070
CREATE OR REPLACE VIEW v_area_5070 AS (
        SELECT id,
	        slug,
	        name,
                ST_SnapToGrid(
                    ST_Transform(
                        geometry,
                        '+proj=aea +lat_0=23 +lon_0=-96 +lat_1=29.5 +lat_2=45.5 +x_0=0 +y_0=0 +datum=NAD83 +units=us-ft +no_defs',
                        5070
                    ),
                    1
                ) AS geometry
        FROM area
    );


-- Function; NOTIFY NEW PRODUCTFILE
CREATE OR REPLACE FUNCTION public.notify_new_productfile ()
  returns trigger
  language plpgsql
AS $$
declare
    channel text := 'cumulus_new_productfile';
begin
	PERFORM (
		WITH payload as (
			SELECT NEW.id AS productfile_id,
				   NEW.product_id  AS product_id,
			       'corpsmap-data' AS s3_bucket,
			       NEW.file        AS s3_key
		)
		SELECT pg_notify(channel, row_to_json(payload)::text)
		FROM payload
	);
	RETURN NULL;
end;
$$;

-- Trigger; NOTIFY STATISTICS ON INSERT
CREATE TRIGGER notify_new_productfile
AFTER INSERT
ON public.productfile
FOR EACH ROW
EXECUTE PROCEDURE public.notify_new_productfile();

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
