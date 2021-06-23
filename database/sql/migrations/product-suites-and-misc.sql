SET search_path TO cumulus,topology,tiger,tiger_data,public;

-- #########################################
-- Add Suite Table 
-- #########################################
CREATE TABLE IF NOT EXISTS suite (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    slug VARCHAR(120) UNIQUE NOT NULL,
    name VARCHAR(120) UNIQUE NOT NULL,
    description TEXT NOT NULL DEFAULT ''
);

-- Add new suites records
INSERT INTO suite (id, name, slug, description) VALUES
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

-- #########################################
-- Alter Products Table 
-- #########################################
-- Remove "name" field
ALTER TABLE product DROP COLUMN name;
-- Add "label" field 
ALTER TABLE product ADD COLUMN label VARCHAR(40);
-- Add "suite_id" field
ALTER TABLE product ADD COLUMN suite_id UUID NOT NULL REFERENCES suite (id);

-- New Products
INSERT INTO product (id, slug, label, temporal_duration, temporal_resolution, dss_fpart, parameter_id, unit_id, description, suite_id) VALUES
    ('a8e3de13-d4fb-4973-a076-c6783c93f332','naefs-mean-qpf-06h','MEAN QPF',21600,21600,'NAEFS-MEAN-QPF','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'Mean QPF 6hr', '87f21790-c192-46d3-88a1-71c4967ef9f0')
    ON CONFLICT DO NOTHING;

INSERT INTO product (id, slug, label, temporal_duration, temporal_resolution, dss_fpart, parameter_id, unit_id, description, suite_id) VALUES    
    ('60f16079-7495-47ab-aa68-36cd6a17fce0','naefs-mean-qtf-06h','MEAN QTF',21600,21600,'NAEFS-MEAN-QTF','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6', 'Mean QTF 6hr', '87f21790-c192-46d3-88a1-71c4967ef9f0')
     ON CONFLICT DO NOTHING;

INSERT INTO product (id, slug, label, temporal_duration, temporal_resolution, dss_fpart, parameter_id, unit_id, description, suite_id) VALUES    
    ('bbfeadbb-1b54-486c-b975-a67d107540f3','mbrfc-krf-fct-airtemp-01h','KRF FCT',3600,3600,'MBRFC-KRF-FCT-AIRTEMP','5fab39b9-90ba-482a-8156-d863ad7c45ad','8f51e5b5-08be-4ea7-9ebc-ad44b465dbc6', 'KRF Forecast AirTemp 1hr', '6b9ac80b-823c-4ac8-bc15-d0232d860302')
    ON CONFLICT DO NOTHING;

INSERT INTO product (id, slug, label, temporal_duration, temporal_resolution, dss_fpart, parameter_id, unit_id, description, suite_id) VALUES    
    ('c96f7a1f-e57d-4694-9d09-451cfa949324','mbrfc-krf-qpf-06h','KRF QPF',21600,21600,'MBRFC-KRF-QPF','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'KRF QPF 6hr', '6b9ac80b-823c-4ac8-bc15-d0232d860302')
    ON CONFLICT DO NOTHING;

INSERT INTO product (id, slug, label, temporal_duration, temporal_resolution, dss_fpart, parameter_id, unit_id, description, suite_id) VALUES       
    ('9890d81e-04c5-45cc-b544-e27fde610501','mbrfc-krf-qpe-01h','KRF QPE',3600,3600,'MBRFC-KRF-QPE','eb82d661-afe6-436a-b0df-2ab0b478a1af','e245d39f-3209-4e58-bfb7-4eae94b3f8dd', 'KRF QPE 1hr', '6b9ac80b-823c-4ac8-bc15-d0232d860302')
    ON CONFLICT DO NOTHING;

-- Update Products, SET "label" and "suite_id" and update "description"
UPDATE product set suite_id='c133e9e7-ddc8-4a98-82d7-880d5db35060' where slug like 'nohrsc-snodas-%';
UPDATE product set suite_id='9252e4e6-18fa-4a33-a3b6-6f99b5e56f13', label='PPT', description='Daily total precipitation (rain+melted snow)' where slug='prism-ppt-early';
UPDATE product set suite_id='9252e4e6-18fa-4a33-a3b6-6f99b5e56f13', label='TMAX', description='Daily maximum temperature [averaged over all days in the month]' where slug='prism-tmax-early';
UPDATE product set suite_id='9252e4e6-18fa-4a33-a3b6-6f99b5e56f13', label='TMIN', description='Daily minimum temperature [averaged over all days in the month]' where slug='prism-tmin-early';
UPDATE product set suite_id='e9730ce6-2ff2-4dbe-ab77-47237a0fd598', label='QPE Pass 1' where slug='ncep-mrms-v12-multisensor-qpe-01h-pass1';
UPDATE product set suite_id='e9730ce6-2ff2-4dbe-ab77-47237a0fd598', label='QPE Pass 2' where slug='ncep-mrms-v12-multisensor-qpe-01h-pass2';
UPDATE product set suite_id='e9d3c98a-6cd7-40cc-9429-57ca7ea96ee1' where slug='ncep-rtma-ru-anl-airtemp';
UPDATE product set suite_id='b35d2f4c-dff2-49bf-9acc-2ed17d3c4576', description='Legacy Product' where slug='ncep-mrms-gaugecorr-qpe-01h';
UPDATE product set suite_id='5d5a280f-0a15-44cd-a11e-694b7cd9f5a5', label='QPF', description='WPC QPF Description Placeholder' where slug='wpc-qpf-2p5km';
UPDATE product set suite_id='3d12bbb0-3a84-409f-90bf-f68fb1ce0bca', description='Legacy Product' where slug in ('ndgd-ltia98-airtemp', 'ndgd-leia98-precip');
UPDATE product set suite_id='74d7191f-7c4b-4549-bf80-5a5de4ba4880', label='MPE', description='CBRFC Multisensor Precipitation Estimates (MPE)' where slug='cbrfc-mpe';
UPDATE product set suite_id='0a4007db-ebcb-4d01-bb3e-3545255da4f0', description='High Resolution Rapid Refresh (HRRR) description' where slug='hrrr-total-precip';
UPDATE product set suite_id='2ba58108-1bdf-4f63-8b47-dfd3590f96ae', label='QPF', description='National Digital Forecast Database (NDFD) QPF 6hr Forecast' where slug='ndfd-conus-qpf-06h';
UPDATE product set suite_id='2ba58108-1bdf-4f63-8b47-dfd3590f96ae', description='National Digital Forecast Database - Forecast 01hr Airtemp' where slug='ndfd-conus-airtemp-01h';
UPDATE product set suite_id='2ba58108-1bdf-4f63-8b47-dfd3590f96ae', description='National Digital Forecast Database - Forecast 03hr Airtemp' where slug='ndfd-conus-airtemp-03h';
UPDATE product set suite_id='2ba58108-1bdf-4f63-8b47-dfd3590f96ae', description='National Digital Forecast Database - Forecast 06hr Airtemp' where slug='ndfd-conus-airtemp-06h';
UPDATE product set suite_id='894205d5-cc55-4071-946b-d4027004cb40' where slug like 'wrf-columbia-%';
UPDATE product set suite_id='c9b39f25-51e5-49cd-9b5a-77c575bebc3b', label='QPF', description='CONUS Forecast Precip' where slug='nbm-co-qpf';
UPDATE product set suite_id='c9b39f25-51e5-49cd-9b5a-77c575bebc3b', label='', description='CONUS Forecast Airtemp' where slug='nbm-co-airtemp';

-- #########################################
-- Update v_products view
-- #########################################
DROP VIEW v_product;

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

-- #########################################
-- Add suite table to roles
-- Re-apply v_product roles
-- #########################################
GRANT SELECT ON
    suite,    
    v_product
TO cumulus_reader;

GRANT INSERT,UPDATE,DELETE ON
    suite,    
    v_product
TO cumulus_writer;

-- #########################################
-- MISC
-- #########################################

-- add new acquirables
INSERT INTO acquirable (id, name, slug) VALUES ('9b10e3fe-db59-4a50-9acb-063fd0cdc435', 'naefs-mean-06h', 'naefs-mean-06h') ON CONFLICT DO NOTHING;    
INSERT INTO acquirable (id, name, slug) VALUES ('a6ba0a12-47d1-4062-995b-3878144fdca4', 'mbrfc-krf-qpe-01h', 'mbrfc-krf-qpe-01h') ON CONFLICT DO NOTHING;
INSERT INTO acquirable (id, name, slug) VALUES ('2c423d07-d085-42ea-ac27-eb007d4d5183', 'mbrfc-krf-qpf-06h', 'mbrfc-krf-qpf-06h') ON CONFLICT DO NOTHING;
INSERT INTO acquirable (id, name, slug) VALUES ('8f0aaa04-11f7-4b39-8b14-d8f0a5f99e44', 'mbrfc-krf-fct-airtemp-01h', 'mbrfc-krf-fct-airtemp-01h') ON CONFLICT DO NOTHING;


-- add tag
INSERT INTO tag (id, name, description, color) VALUES
    ('17308048-d207-43dd-b346-c9836073e911', 'Archive', 'Products not currently updating.', 'dddddd');

-- update tag colors

--Precipitation
UPDATE tag set color = '79b5ff' where id = '726039da-2f21-4393-a15c-5f6e7ea41b1f';
--Temperature
UPDATE tag set color = 'fa7878' where id = '57bda84f-ecec-4cd7-b3b1-c0c36f838a05';
--Snow
UPDATE tag set color = 'd5e7ff' where id = '57bda84f-ecec-4cd7-b3b1-c0c36f838a05';
--Forecast
UPDATE tag set color = '8ffffc' where id = 'cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a';
--Realtime
UPDATE tag set color = '8ffffc' where id = '2d64c718-e7af-41c0-be53-035af341c464';


-- assign product_tags
INSERT INTO product_tags (tag_id, product_id) VALUES ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','e0baa220-1310-445b-816b-6887465cc94b') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','757c809c-dda0-412b-9831-cb9bd0f62d1d') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','57da96dc-fc5e-428c-9318-19f095f461eb') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','86526298-78fa-4307-9276-a7c0a0537d15') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','c2f2f0ed-d120-478a-b38f-427e91ab18e2') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','517369a5-7fe3-4b0a-9ef6-10f26f327b26') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','2274baae-1dcf-4c4c-92bb-e8a640debee0') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','33407c74-cdc2-4ab2-bd9a-3dff99ea02e4') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','e97fbc56-ebe2-4d5a-bcd4-4bf3744d8a1b') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05','10011d9c-04a4-454d-88a0-fb7ba0d64d37') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('d9613031-7cf0-4722-923e-e5c3675a163b','6357a677-5e77-4c37-8aeb-3300707ca885') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('d9613031-7cf0-4722-923e-e5c3675a163b','62e08d34-ff6b-45c9-8bb9-80df922d0779') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('d9613031-7cf0-4722-923e-e5c3675a163b','e4fdadc7-5532-4910-9ed7-3c3690305d86') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('d9613031-7cf0-4722-923e-e5c3675a163b','5e6ca7ed-007d-4944-93aa-0a7a6116bdcd') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('2d64c718-e7af-41c0-be53-035af341c464','c500f609-428f-4c38-b658-e7dde63de2ea') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','002125d6-2c90-4c24-9382-10a535d398bb') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('2d64c718-e7af-41c0-be53-035af341c464','002125d6-2c90-4c24-9382-10a535d398bb') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','d0c1d6f4-cf5d-4332-a17e-dd1757c99c94') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','5317d1c4-c6db-40c2-b527-72f7603be8a0') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','b206a00b-9ed6-42e1-a34d-c67d43828810') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','dde59007-25ec-4bb4-b5e6-8f0f1fbab853') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','f48006a5-ad25-4a9f-9b58-639d75763dd7') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','bbfeadbb-1b54-486c-b975-a67d107540f3') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','c96f7a1f-e57d-4694-9d09-451cfa949324') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','a8e3de13-d4fb-4973-a076-c6783c93f332') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','60f16079-7495-47ab-aa68-36cd6a17fce0') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','84a64026-0e5d-49ac-a48a-6a83efa2b77c') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('cc93b3f9-fbe1-4b35-8f9c-2d1515961c6a','0ac60940-35c2-4c0d-8a3b-49c20e455ff5') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('17308048-d207-43dd-b346-c9836073e911','f1b6ac38-bbc9-48c6-bf78-207005ee74fa') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('17308048-d207-43dd-b346-c9836073e911','793e285f-333b-41a3-b4ab-223a7a764668') ON CONFLICT DO NOTHING;
INSERT INTO product_tags (tag_id, product_id) VALUES ('17308048-d207-43dd-b346-c9836073e911','b50f29f4-547b-4371-9365-60d44eef412e') ON CONFLICT DO NOTHING;
