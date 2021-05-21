-- extensions
CREATE extension IF NOT EXISTS "uuid-ossp";


-- drop tables if they already exist
drop table if exists
    public.product,
    public.productfile,
    public.product_tags,
    public.acquirable,
    public.acquirablefile,
    public.tag
	CASCADE;

-- acquirable
CREATE TABLE IF NOT EXISTS public.acquirable (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(120) NOT NULL,
    slug VARCHAR(120) UNIQUE NOT NULL
);

-- acquirablefile
CREATE TABLE IF NOT EXISTS public.acquirablefile (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    datetime TIMESTAMPTZ NOT NULL,
    file VARCHAR(1200) NOT NULL,
    create_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    process_date TIMESTAMPTZ,
    acquirable_id UUID not null REFERENCES acquirable (id)
);

-- tag
CREATE TABLE IF NOT EXISTS public.tag (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR UNIQUE NOT NULL,
    description VARCHAR,
    color VARCHAR(6) NOT NULL DEFAULT 'A7F3D0'
);

-- product
CREATE TABLE IF NOT EXISTS public.product (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    slug VARCHAR(120) UNIQUE NOT NULL,
    name VARCHAR(120) NOT NULL,
    temporal_duration INTEGER NOT NULL,
    temporal_resolution INTEGER NOT NULL,
    dss_fpart VARCHAR(40),
    parameter_id UUID NOT NULL REFERENCES parameter (id),
    description TEXT NOT NULL DEFAULT '',
    unit_id UUID NOT NULL REFERENCES unit (id),
    deleted boolean NOT NULL DEFAULT false
);

-- product_tags
CREATE TABLE IF NOT EXISTS public.product_tags (
    product_id UUID NOT NULL REFERENCES product(id),
    tag_id UUID NOT NULL REFERENCES tag(id),
    CONSTRAINT unique_tag_product UNIQUE(tag_id,product_id)
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

-- -----
-- VIEWS
-- -----

-- v_acquirablefile
CREATE OR REPLACE VIEW v_acquirablefile AS (
    SELECT a.id           AS acquirable_id,
           a.name         AS acquirable_name,
           a.slug         AS acquirable_slug,
           f.id           AS id,
           f.datetime     AS datetime,
           f.file         AS file,
           f.create_date  AS create_date,
           f.process_date AS process_date
    FROM acquirablefile f
    LEFT JOIN acquirable a ON a.id = f.acquirable_id
);

-- v_product
CREATE OR REPLACE VIEW v_product AS (
    WITH tags_by_product AS (
		SELECT product_id         AS product_id,
               array_agg(tag_id)  AS tags
	    FROM product_tags
	    GROUP BY product_id
	)
	SELECT a.id                             AS id,
           a.slug                           AS slug,
           a.name                           AS name,
           a.temporal_resolution            AS temporal_resolution,
           a.temporal_duration              AS temporal_duration,
           a.dss_fpart                      AS dss_fpart,
           a.description                    AS description,
           COALESCE(t.tags, '{}')           AS tags,
           p.id                             AS parameter_id,
           p.name                           AS parameter,
           u.id                             AS unit_id,
           u.name                           AS unit
	FROM product a
	JOIN unit u ON u.id = a.unit_id
	JOIN parameter p ON p.id = a.parameter_id
	LEFT JOIN tags_by_product t ON t.product_id = a.id
    WHERE NOT a.deleted
);

-- ---------
-- SEED DATA
-- ---------

-- acquirable
INSERT INTO acquirable (id, name, slug) VALUES
    ('d4e67bee-2320-4281-b6ef-a040cdeafeb8', 'hrrr_total_precip','hrrr-total-precip'),
    ('2429db9a-9872-488a-b7e3-de37afc52ca4', 'cbrfc_mpe', 'cbrfc-mpe'),
    ('b27a8724-d34d-4045-aa87-c6d88f9858d0', 'ndgd_ltia98_airtemp', 'ndgd-ltia98-airtemp'),
    ('4d5eb062-5726-4822-9962-f531d9c6caef', 'ndgd_leia98_precip', 'ndgd-leia98-precip'),
    ('87819ceb-72ee-496d-87db-70eb302302dc', 'nohrsc_snodas_unmasked', 'nohrsc-snodas-unmasked'),
    ('099916d1-83af-48ed-85d7-6688ae96023d', 'prism_ppt_early', 'prism-ppt-early'),
    ('97064e4d-453b-4761-8c9a-4a1b979d359e', 'prism_tmax_early', 'prism-tmax-early'),
    ('11e87d14-ec54-4550-bd95-bc6eba0eba08', 'prism_tmin_early', 'prism-tmin-early'),
    ('22678c3d-8ac0-4060-b750-6d27a91d0fb3', 'ncep_rtma_ru_anl_airtemp', 'ncep-rtma-ru-anl-airtemp'),
    ('87a8efb7-af6f-4ece-a97f-53272d1a151d', 'ncep_mrms_v12_multisensor_qpe_01h_pass1', 'ncep-mrms-v12-multisensor-qpe-01h-pass1'),
    ('0c725458-deb7-45bb-84c6-e98083874c0e', 'wpc_qpf_2p5km', 'wpc-qpf-2p5km'),
    ('ccc252f9-defc-4b25-817b-2e14c87073a0', 'ncep_mrms_v12_multisensor_qpe_01h_pass2', 'ncep-mrms-v12-multisensor-qpe-01h-pass2');

-- product
INSERT INTO product (id, name, slug, temporal_duration, temporal_resolution, dss_fpart, parameter_id, unit_id, description) VALUES
    ('e0baa220-1310-445b-816b-6887465cc94b','nohrsc_snodas_snowdepth','nohrsc-snodas-snowdepth', 0,86400,'SNODAS','cfa90543-235c-4266-98c2-26dbc332cd87','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('757c809c-dda0-412b-9831-cb9bd0f62d1d','nohrsc_snodas_swe','nohrsc-snodas-swe',0,86400,'SNODAS','683a55b9-4a94-46b5-9f47-26e66f3037a8','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('57da96dc-fc5e-428c-9318-19f095f461eb','nohrsc_snodas_snowpack_average_temperature','nohrsc-snodas-snowpack-average-temperature',0,86400,'SNODAS','ccc8c81a-ddb0-4738-857b-f0ef69aa1dc0','855ee63c-d623-40d5-a551-3655ce2d7b47', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('86526298-78fa-4307-9276-a7c0a0537d15','nohrsc_snodas_snowmelt','nohrsc-snodas-snowmelt',86400,86400,'SNODAS','d3f49557-2aef-4dc2-a2dd-01b353b301a4','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('c2f2f0ed-d120-478a-b38f-427e91ab18e2','nohrsc_snodas_coldcontent','nohrsc-snodas-coldcontent',0,86400,'SNODAS','2b3f8cf3-d3f5-440b-b7e7-0c8090eda80f','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('517369a5-7fe3-4b0a-9ef6-10f26f327b26','nohrsc_snodas_swe_interpolated','nohrsc-snodas-swe-interpolated',0,86400,'SNODAS-INTERP','683a55b9-4a94-46b5-9f47-26e66f3037a8','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('2274baae-1dcf-4c4c-92bb-e8a640debee0','nohrsc_snodas_snowdepth_interpolated','nohrsc-snodas-snowdepth-interpolated',0,86400,'SNODAS-INTERP','cfa90543-235c-4266-98c2-26dbc332cd87','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('33407c74-cdc2-4ab2-bd9a-3dff99ea02e4','nohrsc_snodas_coldcontent_interpolated','nohrsc-snodas-coldcontent-interpolated',0,86400,'SNODAS-INTERP','2b3f8cf3-d3f5-440b-b7e7-0c8090eda80f','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('e97fbc56-ebe2-4d5a-bcd4-4bf3744d8a1b','nohrsc_snodas_snowpack_average_temperature_interpolated','nohrsc-snodas-snowpack-average-temperature-interpolated',0,86400,'SNODAS-INTERP','ccc8c81a-ddb0-4738-857b-f0ef69aa1dc0','855ee63c-d623-40d5-a551-3655ce2d7b47', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('10011d9c-04a4-454d-88a0-fb7ba0d64d37','nohrsc_snodas_snowmelt_interpolated','nohrsc-snodas-snowmelt-interpolated',86400,86400,'SNODAS-INTERP','d3f49557-2aef-4dc2-a2dd-01b353b301a4','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('64756f41-75e2-40ce-b91a-fda5aeb441fc','prism_ppt_early','prism-ppt-early',86400,86400,'PRISM-EARLY','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('6357a677-5e77-4c37-8aeb-3300707ca885','prism_tmax_early','prism-tmax-early',86400,86400,'PRISM-EARLY','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('62e08d34-ff6b-45c9-8bb9-80df922d0779','prism_tmin_early','prism-tmin-early',86400,86400,'PRISM-EARLY','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('e4fdadc7-5532-4910-9ed7-3c3690305d86','ncep_rtma_ru_anl_airtemp','ncep-rtma-ru-anl-airtemp',0,900,'NCEP-RTMA-RU-ANL','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('f1b6ac38-bbc9-48c6-bf78-207005ee74fa','ncep_mrms_gaugecorr_qpe_01h','ncep-mrms-gaugecorr-qpe-01h',0,3600,'NCEP-MRMS-QPE-GAUGECORR','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('30a6d443-80a5-49cc-beb0-5d3a18a84caa','ncep_mrms_v12_multisensor_qpe_01h_pass1','ncep-mrms-v12-multisensor-qpe-01h-pass1',3600,3600,'NCEP-MRMSV12-QPE-01H-PASS1','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('7c7ba37a-efad-499e-9c3a-5354370b8e9e','ncep_mrms_v12_multisensor_qpe_01h_pass2','ncep-mrms-v12-multisensor-qpe-01h-pass2',3600,3600,'NCEP-MRMSV12-QPE-01H-PASS2','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('0ac60940-35c2-4c0d-8a3b-49c20e455ff5','wpc_qpf_2p5km','wpc-qpf-2p5km',21600,21600,'WPC-QPF-2.5KM','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('5e6ca7ed-007d-4944-93aa-0a7a6116bdcd','ndgd_ltia98_airtemp','ndgd-ltia98-airtemp',0,3600,'NDGD-LTIA98-AIRTEMP','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('1ba5498c-d507-4c82-a80b-9b0af952b02f','ndgd_leia98_precip','ndgd-leia98-precip',3600,3600,'NDGD-LEIA98-PRECIP','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('c500f609-428f-4c38-b658-e7dde63de2ea','cbrfc_mpe','cbrfc-mpe',3600,3600,'CBRFC-MPE','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.'),
    ('002125d6-2c90-4c24-9382-10a535d398bb','hrrr_total_precip','hrrr-total-precip',3600,3600,'HRRR','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus tincidunt nisl sit amet urna mattis, ac ornare sapien volutpat. Nullam laoreet finibus auctor. Donec nisi diam, porttitor et pharetra id, sollicitudin vestibulum dolor. Aliquam porttitor purus non massa ullamcorper, sit amet bibendum risus ornare. Sed ac metus tristique, iaculis arcu a, consequat augue. In id maximus purus. In euismod volutpat velit, a congue est tempor a.');


-- tag
INSERT INTO tag (id, name, description) VALUES
    ('726039da-2f21-4393-a15c-5f6e7ea41b1f', 'Precipitation', 'Products Related to Precipitation'),
    ('d9613031-7cf0-4722-923e-e5c3675a163b', 'Temperature', 'Products Related to Temperature'),
    ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05', 'Snow', 'Products Related to Snow'),
    ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a', 'Forecast', 'Products represent a forecast'),
    ('2d64c718-e7af-41c0-be53-035af341c464', 'Realtime', 'Products constantly updated to support realtime modeling');


-- product_tags
INSERT INTO product_tags (tag_id, product_id) VALUES
    ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','e0baa220-1310-445b-816b-6887465cc94b'),
    ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','757c809c-dda0-412b-9831-cb9bd0f62d1d'),
    ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','57da96dc-fc5e-428c-9318-19f095f461eb'),
    ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','86526298-78fa-4307-9276-a7c0a0537d15'),
    ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','c2f2f0ed-d120-478a-b38f-427e91ab18e2'),
    ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','517369a5-7fe3-4b0a-9ef6-10f26f327b26'),
    ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','2274baae-1dcf-4c4c-92bb-e8a640debee0'),
    ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','33407c74-cdc2-4ab2-bd9a-3dff99ea02e4'),
    ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','e97fbc56-ebe2-4d5a-bcd4-4bf3744d8a1b'),
    ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','10011d9c-04a4-454d-88a0-fb7ba0d64d37'), 
    ('726039da-2f21-4393-a15c-5f6e7ea41b1f','64756f41-75e2-40ce-b91a-fda5aeb441fc'),
    ('d9613031-7cf0-4722-923e-e5c3675a163b','6357a677-5e77-4c37-8aeb-3300707ca885'),
    ('d9613031-7cf0-4722-923e-e5c3675a163b','62e08d34-ff6b-45c9-8bb9-80df922d0779'),
    ('d9613031-7cf0-4722-923e-e5c3675a163b','e4fdadc7-5532-4910-9ed7-3c3690305d86'),
    ('726039da-2f21-4393-a15c-5f6e7ea41b1f','f1b6ac38-bbc9-48c6-bf78-207005ee74fa'),
    ('726039da-2f21-4393-a15c-5f6e7ea41b1f','30a6d443-80a5-49cc-beb0-5d3a18a84caa'),
    ('726039da-2f21-4393-a15c-5f6e7ea41b1f','7c7ba37a-efad-499e-9c3a-5354370b8e9e'),
    ('726039da-2f21-4393-a15c-5f6e7ea41b1f','0ac60940-35c2-4c0d-8a3b-49c20e455ff5'),
    ('d9613031-7cf0-4722-923e-e5c3675a163b','5e6ca7ed-007d-4944-93aa-0a7a6116bdcd'),
    ('726039da-2f21-4393-a15c-5f6e7ea41b1f','1ba5498c-d507-4c82-a80b-9b0af952b02f'),
    ('726039da-2f21-4393-a15c-5f6e7ea41b1f','c500f609-428f-4c38-b658-e7dde63de2ea'),
    ('726039da-2f21-4393-a15c-5f6e7ea41b1f','002125d6-2c90-4c24-9382-10a535d398bb');
