-- extensions
CREATE extension IF NOT EXISTS "uuid-ossp";


-- drop tables if they already exist
drop table if exists
    product,
    productfile,
    product_tags,
    acquirable,
    acquirablefile,
    tag
	CASCADE;

-- acquirable
CREATE TABLE IF NOT EXISTS acquirable (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(120) NOT NULL,
    slug VARCHAR(120) UNIQUE NOT NULL
);

-- acquirablefile
CREATE TABLE IF NOT EXISTS acquirablefile (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    datetime TIMESTAMPTZ NOT NULL,
    file VARCHAR(1200) NOT NULL,
    create_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    process_date TIMESTAMPTZ,
    acquirable_id UUID not null REFERENCES acquirable(id)
);

-- suite
CREATE TABLE IF NOT EXISTS suite (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    slug VARCHAR(120) UNIQUE NOT NULL,
    name VARCHAR(120) UNIQUE NOT NULL,
    description TEXT NOT NULL DEFAULT ''
);

-- tag
CREATE TABLE IF NOT EXISTS tag (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR UNIQUE NOT NULL,
    description VARCHAR,
    color VARCHAR(6) NOT NULL DEFAULT 'A7F3D0'
);

-- product
CREATE TABLE IF NOT EXISTS product (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    slug VARCHAR(120) UNIQUE NOT NULL,
    --name VARCHAR(120) NOT NULL,
    label VARCHAR(40) NOT NULL DEFAULT '',
    temporal_duration INTEGER NOT NULL,
    temporal_resolution INTEGER NOT NULL,
    dss_fpart VARCHAR(40),
    parameter_id UUID NOT NULL REFERENCES parameter (id),
    description TEXT NOT NULL DEFAULT '',
    unit_id UUID NOT NULL REFERENCES unit (id),
    deleted boolean NOT NULL DEFAULT false,
    suite_id UUID NOT NULL REFERENCES suite (id)
);

-- product_tags
CREATE TABLE IF NOT EXISTS product_tags (
    product_id UUID NOT NULL REFERENCES product(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tag(id) ON DELETE CASCADE,
    CONSTRAINT unique_tag_product UNIQUE(tag_id,product_id)
);

-- productfile
CREATE TABLE IF NOT EXISTS productfile (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    datetime TIMESTAMPTZ NOT NULL,
    file VARCHAR(1200) NOT NULL,
    product_id UUID REFERENCES product(id),
    version TIMESTAMPTZ NOT NULL DEFAULT '1111-11-11T11:11:11.11Z',
    acquirablefile_id UUID REFERENCES acquirablefile (id),
    update_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
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
	SELECT a.id                              AS id,
           a.slug                            AS slug,
           CONCAT(
               UPPER(s.slug), ' ', 
               (CASE WHEN LENGTH(a.label) > 1
                     THEN CONCAT(a.label, ' ')
                     ELSE ''
                END), 
                p.name, ' ',
                a.temporal_resolution/60/60, 'hr'
           )                                 AS name,
           a.label                           AS label,
           a.temporal_resolution             AS temporal_resolution,
           a.temporal_duration               AS temporal_duration,
           a.dss_fpart                       AS dss_fpart,
           a.description                     AS description,
           a.suite_id                        AS suite_id,
           s.name                            AS suite,
           COALESCE(t.tags, '{}')            AS tags,
           p.id                              AS parameter_id,
           p.name                            AS parameter,
           u.id                              AS unit_id,
           u.name                            AS unit,
           pf.after                          AS after,
           pf.before                         AS before,
           COALESCE(pf.productfile_count, 0) AS productfile_count
	FROM product a
	JOIN unit u ON u.id = a.unit_id
	JOIN parameter p ON p.id = a.parameter_id
    JOIN suite s ON s.id = a.suite_id
	LEFT JOIN tags_by_product t ON t.product_id = a.id
    LEFT JOIN (
        SELECT product_id    AS product_id,
                COUNT(id)     AS productfile_count,
                MIN(datetime) AS after,
                MAX(datetime) AS before
        FROM productfile
        GROUP BY product_id
    ) AS pf ON pf.product_id = a.id
    WHERE NOT a.deleted
    order by name
);

-- v_productfile
CREATE OR REPLACE VIEW v_productfile AS (
    SELECT p.id           AS product_id,
           p.name         AS product_name,
           p.slug         AS product_slug,
           f.id           AS id,
           f.datetime     AS datetime,
           f.file         AS file,
           f.version      AS version
    FROM productfile f
    LEFT JOIN v_product p ON p.id = f.product_id
);

-- ---------
-- SEED DATA
-- ---------

-- acquirable
INSERT INTO acquirable (id, name, slug) VALUES
    ('fca9e8a4-23e3-471f-a56b-39956055a442', 'lmrfc-qpf-06h', 'lmrfc-qpf-06h'),
    ('660ce26c-9b70-464b-8a17-5c923752545d', 'lmrfc-qpe-01h', 'lmrfc-qpe-01h'),
    ('355d8d9b-1eb4-4f1d-93b7-d77054c5c267', 'serfc-qpf-06h', 'serfc-qpf-06h'),
    ('5365399a-7aa6-4df8-a91a-369ca87c8bd9', 'serfc-qpe-01h', 'serfc-qpe-01h'),
    ('4b0f8d9c-1be4-4605-8265-a076aa6aa555', 'nsidc_ua_swe_sd_v1', 'nsidc-ua-swe-sd-v1'),
    ('9b10e3fe-db59-4a50-9acb-063fd0cdc435', 'naefs-mean-06h', 'naefs-mean-06h'),
    ('a6ba0a12-47d1-4062-995b-3878144fdca4', 'mbrfc-krf-qpe-01h', 'mbrfc-krf-qpe-01h'),
    ('2c423d07-d085-42ea-ac27-eb007d4d5183', 'mbrfc-krf-qpf-06h', 'mbrfc-krf-qpf-06h'),
    ('8f0aaa04-11f7-4b39-8b14-d8f0a5f99e44', 'mbrfc-krf-fct-airtemp-01h', 'mbrfc-krf-fct-airtemp-01h'),
    ('f2fee5df-c51f-4774-bd41-8ded1eed6a64', 'ndfd_conus_qpf_06h', 'ndfd-conus-qpf-06h'),
    ('5c0f1cfa-bcf8-4587-9513-88cb197ec863', 'ndfd_conus_airtemp', 'ndfd-conus-airtemp'),
    ('d4e67bee-2320-4281-b6ef-a040cdeafeb8', 'hrrr_total_precip','hrrr-total-precip'),
    ('ec926de8-6872-4d2b-b7ce-6002221babcd', 'wrf_columbia_precip','wrf-columbia-precip'),
    ('552bf762-449f-4983-bbdc-9d89daada260', 'wrf_columbia_t2_airtemp','wrf-columbia-airtemp'),
    ('d4aa1d8d-ce06-47a0-9768-e817b43a20dd', 'nbm-co-01h', 'nbm-co-01h'),
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

-- suite
INSERT INTO suite (id, name, slug, description) VALUES
    ('91d87306-8eed-45ac-a41e-16d9429ca14c', 'Lower Mississippi River Forecast Center (LMRFC)', 'lmrfc', 'LMRFC Description'),
    ('077600e5-955c-4f0a-8533-7f129366c602', 'Southeast River Forecast Center (SERFC)', 'serfc', 'SERFC Description'),
    ('c5b8cab4-c49a-4b25-82f0-378b84b4eeac', 'National Snow & Ice Data Center (NSIDC)', 'nsidc', E'This data set provides daily 4 km snow water equivalent (SWE) and snow depth over the conterminous United States from 1981 to 2020, developed at the University of Arizona (UA) under the support of the NASA MAP and SMAP Programs. The data were created by assimilating in-situ snow measurements from the National Resources Conservation Service\'s SNOTEL network and the National Weather Service\'s COOP network with modeled, gridded temperature and precipitation data from PRISM.'),
    ('74d7191f-7c4b-4549-bf80-5a5de4ba4880', 'Colorado Basin River Forecast Center (CBRFC)', 'cbrfc', 'CBRFC Description'),
    ('0a4007db-ebcb-4d01-bb3e-3545255da4f0', 'High Resolution Rapid Refresh (HRRR)', 'hrrr', ''),
    ('c133e9e7-ddc8-4a98-82d7-880d5db35060', 'Snow Data Assimilation System (SNODAS)', 'snodas', ''),
    ('c4f403ce-5d02-4f56-9d65-245436831d8d', 'Snow Data Assimilation System (SNODAS) Interpolated', 'snodas-interpolated', ''),
    ('e9d3c98a-6cd7-40cc-9429-57ca7ea96ee1', 'Real-Time Mesoscale Analysis (RTMA) Rapid Update', 'rtma-ru', ''),
    ('b35d2f4c-dff2-49bf-9acc-2ed17d3c4576', 'MultiRadar/MultiSensor (MRMS)', 'mrms', ''),
    ('e9730ce6-2ff2-4dbe-ab77-47237a0fd598', 'MultiRadar/MultiSensor (MRMS) v12', 'mrms-v12', ''),
    ('6b9ac80b-823c-4ac8-bc15-d0232d860302', 'Missouri Basin River Forecast Center', 'mbrfc', 'MBRFC Description...'),
    ('87f21790-c192-46d3-88a1-71c4967ef9f0', 'North American Ensemble Forecast System (NAEFS)', 'naefs', 'The North America Ensemble Forecasting System (NAEFS) is a multinational effort...'),
    ('c9b39f25-51e5-49cd-9b5a-77c575bebc3b', 'National Blend of Models (NBM)', 'nbm', ''),
    ('2ba58108-1bdf-4f63-8b47-dfd3590f96ae', 'National Digital Forecast Database (NDFD)', 'ndfd', ''),
    ('3d12bbb0-3a84-409f-90bf-f68fb1ce0bca', 'National Digital Guidance Database (NDGD)', 'ndgd', ''),
    ('9252e4e6-18fa-4a33-a3b6-6f99b5e56f13', 'PRISM Early', 'prism-early', ''),
    ('5d5a280f-0a15-44cd-a11e-694b7cd9f5a5', 'Weather Prediction Center (WPC)', 'wpc', ''),
    ('894205d5-cc55-4071-946b-d4027004cb40', 'Weather Research and Forecasting Model (WRF) Columbia', 'wrf-columbia', '');

-- suite (description field)
UPDATE suite set description = 'SNODAS is a modeling and data assimilation system developed by the NOHRSC to provide the best possible estimates of snow cover and associated variables to support hydrologic modelling and analysis. The aim of SNODAS is to provide a physically consistent framework to integrate snow data from satellite and airborne platforms, and ground stations with model estimates of snow cover.'
WHERE id = 'c133e9e7-ddc8-4a98-82d7-880d5db35060';

-- product
INSERT INTO product (id, slug, label, temporal_duration, temporal_resolution, dss_fpart, parameter_id, unit_id, description, suite_id) VALUES
    ('1c8c130e-0d3c-4ccc-af5b-d2f95379429c','lmrfc-qpf-06h','LMRFC',21600,21600,'LMRFC QPF 06 HR','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd','Lower Mississippi River Forecast Center 06 hour QPF','91d87306-8eed-45ac-a41e-16d9429ca14c'),
    ('5e13560b-7589-474f-9fd5-bc1cf4163fe4','lmrfc-qpe-01h','LMRFC',3600,3600,'LMRFC QPE 01 HR','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd','Lower Mississippi River Forecast Center 01 hour QPE','91d87306-8eed-45ac-a41e-16d9429ca14c'),
    ('a9a74d32-acdb-4fd2-8478-14d7098c50a7','serfc-qpf-06h','SERFC',21600,21600,'SERFC QPF 06 HR','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd','Southeast River Forecast Center 06 hour QPF','077600e5-955c-4f0a-8533-7f129366c602'),
    ('ae11dad4-7065-4963-8771-7f5aa1e94b5d','serfc-qpe-01h','SERFC', was 3600,3600,'SERFC QPE 01 HR','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd','Southeast River Forecast Center 01 hour QPE','077600e5-955c-4f0a-8533-7f129366c602'),
    ('bf73ae80-22fc-43a2-930a-599531470dc6','nsidc-ua-snowdepth-v1','',0,86400,'NSIDC-UA-SNOWDEPTH-V1','cfa90543-235c-4266-98c2-26dbc332cd87','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'National Snow and Ice Data Center - Snow Depth', 'c5b8cab4-c49a-4b25-82f0-378b84b4eeac'),
    ('87d79a53-5e66-4d31-973c-2adbbe733de2','nsidc-ua-swe-v1','',0,86400,'NSIDC-UA-SWE-V1','683a55b9-4a94-46b5-9f47-26e66f3037a8','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'National Snow and Ice Data Center - SWE', 'c5b8cab4-c49a-4b25-82f0-378b84b4eeac'),
    ('e0baa220-1310-445b-816b-6887465cc94b','nohrsc-snodas-snowdepth','',0,86400,'SNODAS','cfa90543-235c-4266-98c2-26dbc332cd87','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', '', 'c133e9e7-ddc8-4a98-82d7-880d5db35060'),
    ('757c809c-dda0-412b-9831-cb9bd0f62d1d','nohrsc-snodas-swe','',0,86400,'SNODAS','683a55b9-4a94-46b5-9f47-26e66f3037a8','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', '', 'c133e9e7-ddc8-4a98-82d7-880d5db35060'),
    ('57da96dc-fc5e-428c-9318-19f095f461eb','nohrsc-snodas-snowpack-average-temperature','',0,86400,'SNODAS','ccc8c81a-ddb0-4738-857b-f0ef69aa1dc0','855ee63c-d623-40d5-a551-3655ce2d7b47', '', 'c133e9e7-ddc8-4a98-82d7-880d5db35060'),
    ('86526298-78fa-4307-9276-a7c0a0537d15','nohrsc-snodas-snowmelt','',86400,86400,'SNODAS','d3f49557-2aef-4dc2-a2dd-01b353b301a4','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', '', 'c133e9e7-ddc8-4a98-82d7-880d5db35060'),
    ('c2f2f0ed-d120-478a-b38f-427e91ab18e2','nohrsc-snodas-coldcontent','',0,86400,'SNODAS','2b3f8cf3-d3f5-440b-b7e7-0c8090eda80f','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', '', 'c133e9e7-ddc8-4a98-82d7-880d5db35060'),    
    ('517369a5-7fe3-4b0a-9ef6-10f26f327b26','nohrsc-snodas-swe-interpolated','',0,86400,'SNODAS-INTERP','683a55b9-4a94-46b5-9f47-26e66f3037a8','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'SNODAS Interpolated', 'c4f403ce-5d02-4f56-9d65-245436831d8d'),
    ('2274baae-1dcf-4c4c-92bb-e8a640debee0','nohrsc-snodas-snowdepth-interpolated','',0,86400,'SNODAS-INTERP','cfa90543-235c-4266-98c2-26dbc332cd87','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'SNODAS Interpolated', 'c4f403ce-5d02-4f56-9d65-245436831d8d'),
    ('33407c74-cdc2-4ab2-bd9a-3dff99ea02e4','nohrsc-snodas-coldcontent-interpolated','',0,86400,'SNODAS-INTERP','2b3f8cf3-d3f5-440b-b7e7-0c8090eda80f','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'SNODAS Interpolated', 'c4f403ce-5d02-4f56-9d65-245436831d8d'),
    ('e97fbc56-ebe2-4d5a-bcd4-4bf3744d8a1b','nohrsc-snodas-snowpack-average-temperature-interpolated','',0,86400,'SNODAS-INTERP','ccc8c81a-ddb0-4738-857b-f0ef69aa1dc0','855ee63c-d623-40d5-a551-3655ce2d7b47', 'SNODAS Interpolated', 'c4f403ce-5d02-4f56-9d65-245436831d8d'),
    ('10011d9c-04a4-454d-88a0-fb7ba0d64d37','nohrsc-snodas-snowmelt-interpolated','',86400,86400,'SNODAS-INTERP','d3f49557-2aef-4dc2-a2dd-01b353b301a4','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'SNODAS Interpolated', 'c4f403ce-5d02-4f56-9d65-245436831d8d'),    
    ('64756f41-75e2-40ce-b91a-fda5aeb441fc','prism-ppt-early','PPT',86400,86400,'PRISM-EARLY','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Daily total precipitation (rain+melted snow)', '9252e4e6-18fa-4a33-a3b6-6f99b5e56f13'),
    ('6357a677-5e77-4c37-8aeb-3300707ca885','prism-tmax-early','TMAX',86400,86400,'PRISM-EARLY','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6', 'Daily maximum temperature [averaged over all days in the month]', '9252e4e6-18fa-4a33-a3b6-6f99b5e56f13'),
    ('62e08d34-ff6b-45c9-8bb9-80df922d0779','prism-tmin-early','TMIN',86400,86400,'PRISM-EARLY','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6', 'Daily minimum temperature [averaged over all days in the month]', '9252e4e6-18fa-4a33-a3b6-6f99b5e56f13'),    
    ('e4fdadc7-5532-4910-9ed7-3c3690305d86','ncep-rtma-ru-anl-airtemp','',0,900,'NCEP-RTMA-RU-ANL','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6', 'RTMA Description', 'e9d3c98a-6cd7-40cc-9429-57ca7ea96ee1'),    
    ('f1b6ac38-bbc9-48c6-bf78-207005ee74fa','ncep-mrms-gaugecorr-qpe-01h','GAUGECORR QPE',3600,3600,'NCEP-MRMS-QPE-GAUGECORR','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Legacy Product', 'b35d2f4c-dff2-49bf-9acc-2ed17d3c4576'),    
    ('30a6d443-80a5-49cc-beb0-5d3a18a84caa','ncep-mrms-v12-multisensor-qpe-01h-pass1','QPE Pass 1',3600,3600,'NCEP-MRMSV12-QPE-01H-PASS1','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'MRMS Description', 'e9730ce6-2ff2-4dbe-ab77-47237a0fd598'),
    ('7c7ba37a-efad-499e-9c3a-5354370b8e9e','ncep-mrms-v12-multisensor-qpe-01h-pass2','QPE Pass 2',3600,3600,'NCEP-MRMSV12-QPE-01H-PASS2','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'MRMS Description', 'e9730ce6-2ff2-4dbe-ab77-47237a0fd598'),    
    ('0ac60940-35c2-4c0d-8a3b-49c20e455ff5','wpc-qpf-2p5km','QPF',21600,21600,'WPC-QPF-2.5KM','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'WPC QPF Description', '5d5a280f-0a15-44cd-a11e-694b7cd9f5a5'),    
    ('5e6ca7ed-007d-4944-93aa-0a7a6116bdcd','ndgd-ltia98-airtemp','',0,3600,'NDGD-LTIA98-AIRTEMP','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6', 'Legacy Product', '3d12bbb0-3a84-409f-90bf-f68fb1ce0bca'),
    ('1ba5498c-d507-4c82-a80b-9b0af952b02f','ndgd-leia98-precip','',3600,3600,'NDGD-LEIA98-PRECIP','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Legacy Product', '3d12bbb0-3a84-409f-90bf-f68fb1ce0bca'),    
    ('c500f609-428f-4c38-b658-e7dde63de2ea','cbrfc-mpe','MPE',3600,3600,'CBRFC-MPE','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'CBRFC Multisensor Precipitation Estimates (MPE)', '74d7191f-7c4b-4549-bf80-5a5de4ba4880'),
    ('002125d6-2c90-4c24-9382-10a535d398bb','hrrr-total-precip','',3600,3600,'HRRR','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'High Resolution Rapid Refresh (HRRR) description', '0a4007db-ebcb-4d01-bb3e-3545255da4f0'),    
    ('84a64026-0e5d-49ac-a48a-6a83efa2b77c','ndfd-conus-qpf-06h','QPF',21600,21600,'NDFD-CONUS-QPF','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'National Digital Forecast Database (NDFD) QPF 6hr Forecast', '2ba58108-1bdf-4f63-8b47-dfd3590f96ae'),
    ('b206a00b-9ed6-42e1-a34d-c67d43828810','ndfd-conus-airtemp-01h','',3600,3600,'NDFD-CONUS-TEMP','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6', 'National Digital Forecast Database - Forecast 01hr Airtemp', '2ba58108-1bdf-4f63-8b47-dfd3590f96ae'),
    ('dde59007-25ec-4bb4-b5e6-8f0f1fbab853','ndfd-conus-airtemp-03h','',10800,10800,'NDFD-CONUS-TEMP','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6', 'National Digital Forecast Database - Forecast 03hr Airtemp', '2ba58108-1bdf-4f63-8b47-dfd3590f96ae'),
    ('f48006a5-ad25-4a9f-9b58-639d75763dd7','ndfd-conus-airtemp-06h','',21600,21600,'NDFD-CONUS-TEMP','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6', 'National Digital Forecast Database - Forecast 06hr Airtemp', '2ba58108-1bdf-4f63-8b47-dfd3590f96ae'),
    ('b50f29f4-547b-4371-9365-60d44eef412e','wrf-columbia-precip','',3600,3600,'WRF-COLUMBIA','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'WRF Columbia precipitation data created for the entire Columbia River Basin', '894205d5-cc55-4071-946b-d4027004cb40'),
    ('793e285f-333b-41a3-b4ab-223a7a764668','wrf-columbia-airtemp','',3600,3600,'WRF-COLUMBIA','5fab39b9-90ba-482a-8156-d863ad7c45ad','0c8dcd1f-93db-4e64-be1d-47b3462deb2a', 'WRF Columbia T2 (temperature at 2 m) data created for the entire Columbia River Basin', '894205d5-cc55-4071-946b-d4027004cb40'),
    ('5317d1c4-c6db-40c2-b527-72f7603be8a0','nbm-co-qpf','QPF',3600,3600,'NBM-CO-QPF','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'CONUS Forecast Precip', 'c9b39f25-51e5-49cd-9b5a-77c575bebc3b'),
    ('d0c1d6f4-cf5d-4332-a17e-dd1757c99c94','nbm-co-airtemp','',3600,3600,'NBM-CO-AIRTEMP','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6', 'CONUS Forecast Airtemp', 'c9b39f25-51e5-49cd-9b5a-77c575bebc3b'),    
    ('a8e3de13-d4fb-4973-a076-c6783c93f332','naefs-mean-qpf-06h','MEAN QPF',21600,21600,'NAEFS-MEAN-QPF','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Mean QPF 6hr', '87f21790-c192-46d3-88a1-71c4967ef9f0'),
    ('60f16079-7495-47ab-aa68-36cd6a17fce0','naefs-mean-qtf-06h','MEAN QTF',21600,21600,'NAEFS-MEAN-QTF','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6', 'Mean QTF 6hr', '87f21790-c192-46d3-88a1-71c4967ef9f0'),
    ('bbfeadbb-1b54-486c-b975-a67d107540f3','mbrfc-krf-fct-airtemp-01h','KRF FCT',3600,3600,'MBRFC-KRF-FCT-AIRTEMP','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6', 'KRF Forecast AirTemp 1hr', '6b9ac80b-823c-4ac8-bc15-d0232d860302'),
    ('c96f7a1f-e57d-4694-9d09-451cfa949324','mbrfc-krf-qpf-06h','KRF QPF',21600,21600,'MBRFC-KRF-QPF','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'KRF QPF 6hr', '6b9ac80b-823c-4ac8-bc15-d0232d860302'),
    ('9890d81e-04c5-45cc-b544-e27fde610501','mbrfc-krf-qpe-01h','KRF QPE',3600,3600,'MBRFC-KRF-QPE','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'KRF QPE 1hr', '6b9ac80b-823c-4ac8-bc15-d0232d860302');


-- tag
INSERT INTO tag (id, name, description, color) VALUES
    ('726039da-2f21-4393-a15c-5f6e7ea41b1f', 'Precipitation', 'Products Related to Precipitation', '79b5ff'),
    ('d9613031-7cf0-4722-923e-e5c3675a163b', 'Temperature', 'Products Related to Temperature', 'fa7878'),
    ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05', 'Snow', 'Products Related to Snow', 'd5e7ff'),
    ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a', 'Forecast', 'Products represent a forecast', '8ffffc'),
    ('2d64c718-e7af-41c0-be53-035af341c464', 'Realtime', 'Products constantly updated to support realtime modeling', '8ffffc'),
    ('17308048-d207-43dd-b346-c9836073e911', 'Archive', 'Products not currently updating.', 'dddddd');


-- product_tags
INSERT INTO product_tags (tag_id, product_id) VALUES
    ('726039da-2f21-4393-a15c-5f6e7ea41b1f','1c8c130e-0d3c-4ccc-af5b-d2f95379429c'),
    ('726039da-2f21-4393-a15c-5f6e7ea41b1f','5e13560b-7589-474f-9fd5-bc1cf4163fe4'),
    ('726039da-2f21-4393-a15c-5f6e7ea41b1f','a9a74d32-acdb-4fd2-8478-14d7098c50a7'),
    ('726039da-2f21-4393-a15c-5f6e7ea41b1f','ae11dad4-7065-4963-8771-7f5aa1e94b5d'),
    ('726039da-2f21-4393-a15c-5f6e7ea41b1f','a8e3de13-d4fb-4973-a076-c6783c93f332'),
    ('d9613031-7cf0-4722-923e-e5c3675a163b','60f16079-7495-47ab-aa68-36cd6a17fce0'),
    ('d9613031-7cf0-4722-923e-e5c3675a163b','bbfeadbb-1b54-486c-b975-a67d107540f3'),
    ('726039da-2f21-4393-a15c-5f6e7ea41b1f','c96f7a1f-e57d-4694-9d09-451cfa949324'),
    ('726039da-2f21-4393-a15c-5f6e7ea41b1f','9890d81e-04c5-45cc-b544-e27fde610501'),
    ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','bf73ae80-22fc-43a2-930a-599531470dc6'),
    ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','87d79a53-5e66-4d31-973c-2adbbe733de2'),
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
    ('d9613031-7cf0-4722-923e-e5c3675a163b','6357a677-5e77-4c37-8aeb-3300707ca885'),
    ('d9613031-7cf0-4722-923e-e5c3675a163b','62e08d34-ff6b-45c9-8bb9-80df922d0779'),
    ('d9613031-7cf0-4722-923e-e5c3675a163b','e4fdadc7-5532-4910-9ed7-3c3690305d86'),
    ('d9613031-7cf0-4722-923e-e5c3675a163b','5e6ca7ed-007d-4944-93aa-0a7a6116bdcd'),
    ('2d64c718-e7af-41c0-be53-035af341c464','c500f609-428f-4c38-b658-e7dde63de2ea'),
    ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','002125d6-2c90-4c24-9382-10a535d398bb'),
    ('2d64c718-e7af-41c0-be53-035af341c464','002125d6-2c90-4c24-9382-10a535d398bb'),
    ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','d0c1d6f4-cf5d-4332-a17e-dd1757c99c94'),
    ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','5317d1c4-c6db-40c2-b527-72f7603be8a0'),
    ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','b206a00b-9ed6-42e1-a34d-c67d43828810'),
    ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','dde59007-25ec-4bb4-b5e6-8f0f1fbab853'),
    ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','f48006a5-ad25-4a9f-9b58-639d75763dd7'),
    ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','bbfeadbb-1b54-486c-b975-a67d107540f3'),
    ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','c96f7a1f-e57d-4694-9d09-451cfa949324'),
    ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','a8e3de13-d4fb-4973-a076-c6783c93f332'),
    ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','60f16079-7495-47ab-aa68-36cd6a17fce0'),
    ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','84a64026-0e5d-49ac-a48a-6a83efa2b77c'),
    ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','0ac60940-35c2-4c0d-8a3b-49c20e455ff5'),
    ('17308048-d207-43dd-b346-c9836073e911','f1b6ac38-bbc9-48c6-bf78-207005ee74fa'),
    ('17308048-d207-43dd-b346-c9836073e911','793e285f-333b-41a3-b4ab-223a7a764668'),
    ('17308048-d207-43dd-b346-c9836073e911','b50f29f4-547b-4371-9365-60d44eef412e');
