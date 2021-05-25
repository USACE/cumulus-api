-- extensions
CREATE extension IF NOT EXISTS "uuid-ossp";


-- drop tables if they already exist
drop table if exists
    office,
    watershed,
    watershed_roles,
    my_watersheds,
    area,
    area_group,
	role
	CASCADE;


-- office
CREATE TABLE IF NOT EXISTS office (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    symbol VARCHAR(120) UNIQUE NOT NULL,
    name VARCHAR(120) UNIQUE NOT NULL
);

-- watershed
CREATE TABLE IF NOT EXISTS watershed (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    slug VARCHAR UNIQUE NOT NULL,
    name VARCHAR,
    geometry geometry,
    office_id UUID REFERENCES office(id),
	deleted boolean NOT NULL DEFAULT false
);

-- my_watersheds
CREATE TABLE IF NOT EXISTS my_watersheds (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    watershed_id UUID NOT NULL REFERENCES watershed(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES profile(id) ON DELETE CASCADE,
    CONSTRAINT profile_unique_watershed UNIQUE(watershed_id, profile_id)
);

-- area_group
CREATE TABLE IF NOT EXISTS area_group (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    watershed_id UUID NOT NULL REFERENCES watershed(id) ON DELETE CASCADE,
    slug VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    CONSTRAINT watershed_unique_slug UNIQUE(watershed_id, slug),
    CONSTRAINT watershed_unique_name UNIQUE(watershed_id, name)
);

-- area
CREATE TABLE IF NOT EXISTS area (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    slug VARCHAR UNIQUE NOT NULL,
    name VARCHAR UNIQUE NOT NULL,
    geometry geometry NOT NULL,
    area_group_id UUID NOT NULL REFERENCES area_group(id) ON DELETE CASCADE,
    CONSTRAINT area_group_unique_slug UNIQUE(area_group_id, slug),
    CONSTRAINT area_group_unique_name UNIQUE(area_group_id, name)
);


------------------------
-- Watershed Permissions
------------------------
-- role
CREATE TABLE IF NOT EXISTS role (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR NOT NULL
);
INSERT INTO role (id, name) VALUES
    ('37f14863-8f3b-44ca-8deb-4b74ce8a8a69', 'ADMIN'),
    ('2962bdde-7007-4ba0-943f-cb8e72e90704', 'MEMBER');

-- watershed_roles
CREATE TABLE IF NOT EXISTS watershed_roles (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profile(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES role(id) ON DELETE CASCADE,
    watershed_id UUID NOT NULL REFERENCES watershed(id) ON DELETE CASCADE,
    granted_by UUID REFERENCES profile(id),
    granted_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_watershed_role UNIQUE(profile_id,watershed_id,role_id)
);

-- -----
-- VIEWS
-- -----

CREATE OR REPLACE VIEW v_watershed AS (
    SELECT w.id,
           w.slug,
           w.name,
           w.geometry AS geometry,
           COALESCE(ag.area_groups, '{}') AS area_groups,
           f.symbol AS office_symbol
	FROM   watershed w
	LEFT JOIN (
		SELECT array_agg(id) as area_groups, watershed_id
		FROM area_group
		GROUP BY watershed_id
	) ag ON ag.watershed_id = w.id
    LEFT JOIN office f ON w.office_id = f.id
	WHERE NOT w.deleted
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

-- v_watershed_roles
CREATE OR REPLACE VIEW v_watershed_roles AS (
    SELECT a.id,
           a.profile_id,
           b.edipi,
           b.username,
           b.email,
           b.is_admin,
           c.id AS watershed_id,
           r.id   AS role_id,
           r.name AS role,
           UPPER(c.slug || '.' || r.name) AS rolename
    FROM watershed_roles a
    INNER JOIN profile b ON b.id = a.profile_id
    INNER JOIN watershed c ON c.id = a.watershed_id AND NOT c.deleted
    INNER JOIN role    r ON r.id = a.role_id
    ORDER BY username, role
);

-- v_profile
-- create statement here because watershed and watershed_roles
-- tables must exist before creating this view
CREATE OR REPLACE VIEW v_profile AS (
    WITH roles_by_profile AS (
        SELECT profile_id,
               array_agg(UPPER(b.slug || '.' || c.name)) AS roles
        FROM watershed_roles a
        INNER JOIN watershed b ON a.watershed_id = b.id AND NOT b.deleted
        INNER JOIN role      c ON a.role_id    = c.id
        GROUP BY profile_id
    )
    SELECT p.id,
           p.edipi,
           p.username,
           p.email,
           p.is_admin,
           COALESCE(r.roles,'{}') AS roles
    FROM profile p
    LEFT JOIN roles_by_profile r ON r.profile_id = p.id
);

-- ---------
-- Seed Data
------------

-- office
INSERT INTO office (id, symbol, name) VALUES
    ('0088df5f-ec58-4654-9b71-3590266b475c','MVS','St. Louis District'),
    ('0360bb56-92f8-4c1e-9b08-8396b216f2d3','LRDO','Ohio River Region'),
    ('07c1c91e-2e42-4fbc-a550-f775a27eb419','NWK','Kansas City District'),
    ('098c898f-7f0f-44e8-b2c1-329d7dd50166','SAW','Wilmington District'),
    ('0cac2b45-a5df-49b3-9176-7d5145681958','NAD','North Atlantic Division'),
    ('1f579664-d1db-4ee9-897e-47c16dc55012','NWO','Omaha District'),
    ('2222f2f5-d512-41ee-83d7-3a6cfcbf5bfb','SPD','South Pacific Division'),
    ('26dab361-76a0-4cb2-b5a5-01667ab7f7da','MVN','New Orleans District'),
    ('26e6c300-480b-4e22-afae-7cc27dd9b116','SWT','Tulsa District'),
    ('33f03e9a-711b-41e7-9bdd-66152b69128d','MVP','St. Paul District'),
    ('4142c26c-0407-41ad-b660-8657ddb2be69','SAJ','Jacksonville District'),
    ('4f4f6899-cac1-402f-adee-8109d5bc5db3','SWG','Galveston District'),
    ('4ffaa895-0f05-4b59-8d12-86c901e2f229','LRN','Nashville District'),
    ('586ac79a-083e-4c8c-8438-9585a88a4b3d','LRE','Detroit District'),
    ('60754640-fef3-429b-b2f4-efdcf3b61e55','SWL','Little Rock District'),
    ('60c46088-9c98-4927-991d-0bd126bbb62e','LRB','Buffalo District'),
    ('64fb2c2f-e59a-44cc-a54d-22e8d7c909a0','NAE','New England District'),
    ('6e3c2e48-a15a-4892-ba91-caab86499abc','NAP','Philadelphia District'),
    ('74f7b6ff-b026-4272-b44a-cb1d536e1b8d','POD','Pacific Ocean Division'),
    ('76bb611e-3fbf-4779-b251-203de3502670','SPN','San Francisco District'),
    ('788cc853-235a-4e43-a136-b1f190a6a656','LRH','Huntington District'),
    ('790ec8cf-8dad-48c9-bea9-9b8c26d29471','SAD','South Atlantic Division'),
    ('7d7e962d-e554-48f0-8f82-b762a31441a6','NAB','Baltimore District'),
    ('7fd53614-f484-4dfd-8fc4-d11b11fb071c','NAO','Norfolk District'),
    ('834ea54d-2454-425f-b443-50ba4ab46e28','NWW','Walla Walla District'),
    ('85ba21d8-ba4b-4060-a519-a3e69c1e29ed','NWDP','Pacific Northwest Region'),
    ('89a1fe0c-03f3-47cf-8ee1-cd3de2e1ba7b','SPL','Los Angeles District'),
    ('8fc88b15-9cd4-4e86-8b8c-6d956926010b','MVM','Memphis District'),
    ('90173658-2de9-4329-926d-176c1b29089a','NWDM','Missouri River Region'),
    ('90b958ea-0076-4925-87d8-670eb7da5551','SAS','Savannah District'),
    ('99322682-b22f-4c47-972a-81c4d782b0d5','SAC','Charleston District'),
    ('99a6b349-535a-4aab-b742-9bdd145461e7','LRDG','Great Lakes Region'),
    ('9a631b0c-d8ad-4411-8220-04683c9c24f4','POH','Hawaii District'),
    ('a0baec43-2817-4161-b654-c3c513b5276b','POA','Alaska District'),
    ('a222e733-2fa7-4cd8-b3a6-065956e693f0','SWF','Fort Worth District'),
    ('a9929dc4-7d7c-4ddb-b727-d752137ffc10','SPA','Albuquerque District'),
    ('b952664c-4b11-4d85-89fa-a2cc405b1131','LRL','Louisville District'),
    ('b9c56905-9dad-4418-9654-d1fcd9b3a57f','MVR','Rock Island District'),
    ('c18588b6-25ab-42c9-b31a-a33c585d0b49','NWP','Portland District'),
    ('c88758e9-4575-44b0-9d38-b6c0ee909061','NWS','Seattle District'),
    ('d02f876f-eb00-425b-aeca-09fa105d5bc2','MVK','Vicksburg District'),
    ('d0b7ddca-a321-44bd-bf2c-059c9c8cbe23','LRD','Great Lakes and Ohio River Division'),
    ('d3da00c9-f839-4add-90a9-73053292d196','NWD','Northwestern Division'),
    ('dd580032-c210-4f98-8ab7-bda92ff2fe5e','MVD','Mississippi Valley Division'),
    ('df64a2de-91a2-4e6c-85c9-53d3d03f6794','SPK','Sacramento District'),
    ('e7c9cfe8-99eb-4845-a058-46e53a75b28b','LRP','Pittsburgh District'),
    ('eb545b18-5498-43c8-8652-f73e16446cc0','SAM','Mobile District'),
    ('ede616b6-5ab7-42c6-9489-7c09bfb6a54b','NAN','New York District'),
    ('fa9b344c-911c-43e9-966c-b0e1357e385c','LRC','Chicago District'),
    ('fe551ee7-3b04-440c-89a4-162dffd99ed2','SWD','Southwestern Division'),
    ('cf0e2fde-9156-4a96-a8bc-32640cb0043d','STUDY','Columbia  Study'),
-- ('6757366f-136f-4233-98eb-e700a167bff5','EL','Environmental Laboratory'),
-- ('9db3328b-73d9-4eb2-be67-79667173348a','WPC','Western Processing Center'),
-- ('9efd790c-ad0f-4ff3-943d-c66e5dd631b8','HEC','Hydrologic Engineering Cennter'),
-- ('b220e75d-29ad-45cf-8e34-b23648735654','CERL','Construction Engineering Research Laboratory'),
-- ('ca6aa6f6-48ce-4532-b514-12a4464bdbe9','WCSC','Waterborne Commerce Statistics Center'),

-- ('e03caac3-9e58-4cab-83bc-e2b6ad746124','IWR','Institute for Water Resources'),
('e303450f-af6a-4272-a262-fdb94f8e3e86','SERFC','Southeast River Forecast Center');
-- ('e8932733-872b-471d-9b81-6212b574da6d','LCRA','Lower Colorado River Authority'),
-- ('fa8020b3-01ad-4ad1-859b-39fa883fc1eb','CRREL','Cold Regions Research and Engineering Lab'),
-- ('1921eb45-d66d-42e0-a5a3-521bcc8d060e','ITL','Information Technology Laboratory'),
-- ('28e05c71-e74b-4e64-bf69-252977ea9317','NDC','Navigation Data Center'),
-- ('29e3de84-039d-4a9d-8623-e9a94ba4f710','CPC','Central Processing Center'),
-- ('2d680d7f-3c62-4147-ab25-e5a288188aa9','HQ','Headquarters'),
-- ('3ef77886-5fe6-4176-b740-1d72b18143dd','CWMS','All CWMS Offices'),
-- ('5df16d60-00d7-4e03-afa6-8968baa0528d','GSL','Geotechnical and Structures Laboratory'),
-- ('5e2d70fa-cbb8-4759-903b-cf4bd8318aa1','CHL','Coastal and Hydraulics Laboratory'),
-- ('604c23ed-62a4-4c25-b613-f3d7e46b05ef','TEC','Topographic Engineering Center'),
-- ('6b58ce44-bcb9-4780-9860-1368b4371394','UNK','Corps of Engineers Office Unknown'),
-- ('7c18d4e5-a999-4c9e-a36a-9c89f2278891','ERD','Engineer Research and Development Center'),



-- extent to polygon reference order - simple 4 point extents
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
	 ('01313583-8fed-4235-8cf2-df5fe23b4b2a','hatchie-river','Hatchie River',ST_GeomFromText('POLYGON ((542000 1444000, 694000 1444000, 694000 1296000, 542000 1296000, 542000 1444000))',5070),'8fc88b15-9cd4-4e86-8b8c-6d956926010b'),
	 ('03206ff6-fe91-426c-a5e9-4c651b06f9c6','eau-galla-river','Eau Galla River',ST_GeomFromText('POLYGON ((284000 2460000, 326000 2460000, 326000 2404000, 284000 2404000, 284000 2460000))',5070),'33f03e9a-711b-41e7-9bdd-66152b69128d'),
	 ('048ce853-6642-4ac4-9fb2-81c01f67a85b','mississippi-river-headwaters','Mississippi River Headwaters',ST_GeomFromText('POLYGON ((24000 2760000, 254000 2760000, 254000 2402000, 24000 2402000, 24000 2760000))',5070),'33f03e9a-711b-41e7-9bdd-66152b69128d'),
	 ('0573081e-c72c-4bf9-9709-7f62ecd80a64','bill-williams-river','Bill Williams River',ST_GeomFromText('POLYGON ((-1652000 1522000, -1494000 1522000, -1494000 1354000, -1652000 1354000, -1652000 1522000))',5070),'89a1fe0c-03f3-47cf-8ee1-cd3de2e1ba7b'),
	 ('070204a3-66d9-471c-bd6e-ab59ea0858bb','crooked-river','Crooked River',ST_GeomFromText('POLYGON ((-2006000 2668000, -1854000 2668000, -1854000 2512000, -2006000 2512000, -2006000 2668000))',5070),'c18588b6-25ab-42c9-b31a-a33c585d0b49'),
	 ('074ff6ed-69b1-4958-87a5-9cd68fde7030','upper-ohio-river','Upper Ohio River',ST_GeomFromText('POLYGON ((1244000 1976000, 1300000 1976000, 1300000 1942000, 1244000 1942000, 1244000 1976000))',5070),'e7c9cfe8-99eb-4845-a058-46e53a75b28b'),
	 ('08ee0918-b869-46c5-b9fd-e02f88ceff64','green-river','Green River',ST_GeomFromText('POLYGON ((-1980000 3010000, -1900000 3010000, -1900000 2934000, -1980000 2934000, -1980000 3010000))',5070),'c88758e9-4575-44b0-9d38-b6c0ee909061'),
	 ('0c06e6d6-68f3-4943-a95e-22ef82696e7e','connecticut-river','Connecticut River',ST_GeomFromText('POLYGON ((1820000 2734000, 1958000 2734000, 1958000 2266000, 1820000 2266000, 1820000 2734000))',5070),'64fb2c2f-e59a-44cc-a54d-22e8d7c909a0'),
	 ('0d53c4da-8712-4e99-9824-1695e3e1966c','rio-hondo','Rio Hondo',ST_GeomFromText('POLYGON ((-914000 1226000, -770000 1226000, -770000 1158000, -914000 1158000, -914000 1226000))',5070),'a9929dc4-7d7c-4ddb-b727-d752137ffc10'),
	 ('0f065e6a-3380-4ac3-b576-89fae7774b9f','little-sandy-river','Little Sandy River',ST_GeomFromText('POLYGON ((1096000 1812000, 1158000 1812000, 1158000 1732000, 1096000 1732000, 1096000 1812000))',5070),'788cc853-235a-4e43-a136-b1f190a6a656'),
	 ('11cddcb1-aca6-4398-b5bd-f10e19826c16','tranquitas-creek','Tranquitas Creek',ST_GeomFromText('POLYGON ((-214000 522000, -174000 522000, -174000 488000, -214000 488000, -214000 522000))',5070),'4f4f6899-cac1-402f-adee-8109d5bc5db3'),
	 ('11e92768-81ed-4b62-9179-1f010ac9bb97','thames-river','Thames River',ST_GeomFromText('POLYGON ((1916000 2396000, 1992000 2396000, 1992000 2268000, 1916000 2268000, 1916000 2396000))',5070),'64fb2c2f-e59a-44cc-a54d-22e8d7c909a0'),
	 ('14c56e44-c8aa-4f89-a226-3e99e181d522','neches-river','Neches River',ST_GeomFromText('POLYGON ((-42000 1144000, 276000 1144000, 276000 724000, -42000 724000, -42000 1144000))',5070),'a222e733-2fa7-4cd8-b3a6-065956e693f0'),
	 ('14eb04fc-7eb8-4322-a2a0-999e371ca989','cowlitz-river','Cowlitz River',ST_GeomFromText('POLYGON ((-2070000 2922000, -1918000 2922000, -1918000 2838000, -2070000 2838000, -2070000 2922000))',5070),'c18588b6-25ab-42c9-b31a-a33c585d0b49'),
	 ('151d8075-a6b7-45f2-92ed-360b4f7f7b47','area-3','Area 3',ST_GeomFromText('POLYGON ((1514000 498000, 1572000 498000, 1572000 418000, 1514000 418000, 1514000 498000))',5070),'4142c26c-0407-41ad-b660-8657ddb2be69'),
	 ('1572c0a6-e9b9-420a-85dc-ae9d9ac8f958','housatonic-river','Housatonic River',ST_GeomFromText('POLYGON ((1820000 2404000, 1896000 2404000, 1896000 2240000, 1820000 2240000, 1820000 2404000))',5070),'64fb2c2f-e59a-44cc-a54d-22e8d7c909a0'),
	 ('15e50ede-337b-4bbf-a6fa-1be57d1b8715','above-fort-peck','Above Fort Peck',ST_GeomFromText('POLYGON ((-1394000 2998000, -740000 2998000, -740000 2460000, -1394000 2460000, -1394000 2998000))',5070),'1f579664-d1db-4ee9-897e-47c16dc55012'),
	 ('1731a851-8813-458f-8e3c-ef7e0bb0a285','farm-river','Farm River',ST_GeomFromText('POLYGON ((518000 2104000, 614000 2104000, 614000 1968000, 518000 1968000, 518000 2104000))',5070),'b9c56905-9dad-4418-9654-d1fcd9b3a57f'),
	 ('ec1494d2-bcca-437c-9a3f-bea84f0b63db','oahe-to-gavins', 'Oahe to Gavins', ST_GeomFromText('POLYGON ((-722000 2452000, -112400 2452000, -112400 2114000, -722000 2114000 , -722000 2452000))',5070), '90173658-2de9-4329-926d-176c1b29089a'),	 
	 ('1a629fac-82c9-4b3e-b7fc-6a891d944140','ohio-river','Ohio River',ST_GeomFromText('POLYGON ((1006000 1914000, 1206000 1914000, 1206000 1754000, 1006000 1754000, 1006000 1914000))',5070),'788cc853-235a-4e43-a136-b1f190a6a656'),
	 ('1b8cb00f-768a-4dac-81cb-dce6a06bd578','lavaca-river','Lavaca River',ST_GeomFromText('POLYGON ((-126000 756000, -20000 756000, -20000 620000, -126000 620000, -126000 756000))',5070),'4f4f6899-cac1-402f-adee-8109d5bc5db3'),
	 ('1c54fbe9-b4d3-4da3-919c-e448c6ace0ef','yadkin-river','Yadkin River',ST_GeomFromText('POLYGON ((1270000 1630000, 1420000 1630000, 1420000 1526000, 1270000 1526000, 1270000 1630000))',5070),'098c898f-7f0f-44e8-b2c1-329d7dd50166'),
	 ('1d31054f-3f50-49da-8c81-7a1d8a36cc58','providence-river','Providence River',ST_GeomFromText('POLYGON ((1982000 2370000, 2022000 2370000, 2022000 2336000, 1982000 2336000, 1982000 2370000))',5070),'64fb2c2f-e59a-44cc-a54d-22e8d7c909a0'),
	 ('225faeef-4251-4e97-9901-2c3c480180d3','mississippi-river','Mississippi River',ST_GeomFromText('POLYGON ((400000 1860000, 610000 1860000, 610000 1564000, 400000 1564000, 400000 1860000))',5070),'0088df5f-ec58-4654-9b71-3590266b475c'),
	 ('24352135-cac5-4dfd-b230-03d17aa97207','tualatin-river','Tualatin River',ST_GeomFromText('POLYGON ((-2120000 2838000, -2054000 2838000, -2054000 2770000, -2120000 2770000, -2120000 2838000))',5070),'c18588b6-25ab-42c9-b31a-a33c585d0b49'),
	 ('2778d7eb-5ef6-419a-823d-3cf5a1cdad0b','columbia-river','Columbia River',ST_GeomFromText('POLYGON ((-1942000 3278000, -1442000 3278000, -1442000 2782000, -1942000 2782000, -1942000 3278000))',5070),'c88758e9-4575-44b0-9d38-b6c0ee909061'),
	 ('28a9e9ac-ee2c-436e-8d22-79b97bf8ede5','santee-cooper-river','Santee Cooper River',ST_GeomFromText('POLYGON ((1186000 1556000, 1566000 1556000, 1566000 1184000, 1186000 1184000, 1186000 1556000))',5070),'99322682-b22f-4c47-972a-81c4d782b0d5'),
	 ('29903d34-5f0f-438f-8a18-9e74c9f8e3d6','passaic-river','Passaic River',ST_GeomFromText('POLYGON ((1754000 2254000, 1830000 2254000, 1830000 2152000, 1754000 2152000, 1754000 2254000))',5070),'6e3c2e48-a15a-4892-ba91-caab86499abc'),
	 ('29ba9a1e-82fe-4080-986c-d54e4f782740','lower-mississippi-river-1','Lower Mississippi River',ST_GeomFromText('POLYGON ((304000 1210000, 704000 1210000, 704000 660000, 304000 660000, 304000 1210000))',5070),'26dab361-76a0-4cb2-b5a5-01667ab7f7da'),
	 ('2c299ae4-be52-4987-bb84-2eaa425b7845','upper-columbia','Upper Columbia',ST_GeomFromText('POLYGON ((-1640000 3506000, -1418000 3506000, -1418000 3082000, -1640000 3082000, -1640000 3506000))',5070),'cf0e2fde-9156-4a96-a8bc-32640cb0043d'),
	 ('2d627ea7-ac70-403b-8f1d-bd1015070f61','upper-wabash-river','Upper Wabash River',ST_GeomFromText('POLYGON ((730000 2090000, 978000 2090000, 978000 1946000, 730000 1946000, 730000 2090000))',5070),'b952664c-4b11-4d85-89fa-a2cc405b1131'),
	 ('2fba3761-9d97-42a0-bb63-118b369b9b8f','nonconnah-creek','Nonconnah Creek',ST_GeomFromText('POLYGON ((528000 1364000, 586000 1364000, 586000 1334000, 528000 1334000, 528000 1364000))',5070),'8fc88b15-9cd4-4e86-8b8c-6d956926010b'),
	 ('30e3008b-0b72-4ac2-99ff-fbe751934cc1','monongahela-river','Monongahela River',ST_GeomFromText('POLYGON ((1306000 2064000, 1448000 2064000, 1448000 1818000, 1306000 1818000, 1306000 2064000))',5070),'e7c9cfe8-99eb-4845-a058-46e53a75b28b'),
	 ('3350e9e3-2464-49c3-9843-ebd1bdfb58c5','nueces-river','Nueces River',ST_GeomFromText('POLYGON ((-446000 798000, -144000 798000, -144000 496000, -446000 496000, -446000 798000))',5070),'4f4f6899-cac1-402f-adee-8109d5bc5db3'),
	 ('3413594d-8f1b-4d41-b48a-33447771a44d','middle-wabash-river','Middle Wabash River',ST_GeomFromText('POLYGON ((708000 1982000, 942000 1982000, 942000 1714000, 708000 1714000, 708000 1982000))',5070),'b952664c-4b11-4d85-89fa-a2cc405b1131'),
	 ('39e7ef95-27d6-47a0-88a9-161039a1cbcf','st-francis-river','St Francis River',ST_GeomFromText('POLYGON ((454000 1944000, 670000 1944000, 670000 1450000, 454000 1450000, 454000 1944000))',5070),'0088df5f-ec58-4654-9b71-3590266b475c'),
	 ('3b24f68a-662b-46da-afd7-33d537496fef','cedar-river','Cedar River',ST_GeomFromText('POLYGON ((-1976000 3046000, -1906000 3046000, -1906000 2950000, -1976000 2950000, -1976000 3046000))',5070),'c88758e9-4575-44b0-9d38-b6c0ee909061'),
	 ('3b2a4a71-dd37-4b07-b241-5412d1649051','meramec-river','Meramec River',ST_GeomFromText('POLYGON ((360000 1752000, 500000 1752000, 500000 1612000, 360000 1612000, 360000 1752000))',5070),'0088df5f-ec58-4654-9b71-3590266b475c'),
	 ('3b71f09e-1f16-43e3-b700-df319f0be9ef','mill-creek','Mill Creek',ST_GeomFromText('POLYGON ((-1766000 2820000, -1654000 2820000, -1654000 2726000, -1766000 2726000, -1766000 2820000))',5070),'834ea54d-2454-425f-b443-50ba4ab46e28'),
	 ('3bfc0f1a-49c9-4c27-a990-924d5255a926','ouachita-black-river','Ouachita Black River',ST_GeomFromText('POLYGON ((146000 1322000, 480000 1322000, 480000 902000, 146000 902000, 146000 1322000))',5070),'d02f876f-eb00-425b-aeca-09fa105d5bc2'),
	 ('3cce6d54-5e86-4455-b426-6d2d2a2045ca','chehalis-river','Chehalis River',ST_GeomFromText('POLYGON ((-2104000 3032000, -1998000 3032000, -1998000 2886000, -2104000 2886000, -2104000 3032000))',5070),'c88758e9-4575-44b0-9d38-b6c0ee909061'),
	 ('3e322a11-b76b-4710-8f9a-b7884cd8ae77','big-sandy-river','Big Sandy River',ST_GeomFromText('POLYGON ((1114000 1796000, 1288000 1796000, 1288000 1624000, 1114000 1624000, 1114000 1796000))',5070),'788cc853-235a-4e43-a136-b1f190a6a656'),
	 ('3e8db268-d9ca-47ec-ae93-21a3c2bcf0a1','kootenai','Kootenai',ST_GeomFromText('POLYGON ((-1604000 3298000, -1350000 3298000, -1350000 2910000, -1604000 2910000, -1604000 3298000))',5070),'cf0e2fde-9156-4a96-a8bc-32640cb0043d'),
	 ('426c4e4c-4654-41af-b5e3-2597abc06cb4','lehigh-river','Lehigh River',ST_GeomFromText('POLYGON ((1654000 2220000, 1734000 2220000, 1734000 2116000, 1654000 2116000, 1654000 2220000))',5070),'6e3c2e48-a15a-4892-ba91-caab86499abc'),
	 ('43f38b7d-0d25-4d6e-a333-aa0d5408c4a1','little-miami-river','Little Miami River',ST_GeomFromText('POLYGON ((980000 1952000, 1058000 1952000, 1058000 1824000, 980000 1824000, 980000 1952000))',5070),'b952664c-4b11-4d85-89fa-a2cc405b1131'),
	 ('442e9ee0-d1d1-4f30-94b6-17d2bdcfe8f2','west-branch-susquehanna-river','West Branch Susquehanna River',ST_GeomFromText('POLYGON ((1418000 2252000, 1632000 2252000, 1632000 2066000, 1418000 2066000, 1418000 2252000))',5070),'7d7e962d-e554-48f0-8f82-b762a31441a6'),
	 ('4837ce40-c5de-4bac-8986-48497bd96c4a','upper-snake-river','Upper Snake River',ST_GeomFromText('POLYGON ((-1592000 2522000, -1098000 2522000, -1098000 2198000, -1592000 2198000, -1592000 2522000))',5070),'834ea54d-2454-425f-b443-50ba4ab46e28'),
	 ('483ef939-a7a6-45f0-85f0-019f0f64096c','beaver-river','Beaver River',ST_GeomFromText('POLYGON ((1216000 2194000, 1356000 2194000, 1356000 1944000, 1216000 1944000, 1216000 2194000))',5070),'e7c9cfe8-99eb-4845-a058-46e53a75b28b'),
	 ('49200a82-fba3-458e-8929-e5c8b5e4f726','willamette-river','Willamette River',ST_GeomFromText('POLYGON ((-2174000 2850000, -1988000 2850000, -1988000 2548000, -2174000 2548000, -2174000 2850000))',5070),'c18588b6-25ab-42c9-b31a-a33c585d0b49'),
	 ('4a416b1c-c766-4b9d-a40e-15e9b05744c4','kaskaskia-river','Kaskaskia River',ST_GeomFromText('POLYGON ((498000 1938000, 670000 1938000, 670000 1672000, 498000 1672000, 498000 1938000))',5070),'0088df5f-ec58-4654-9b71-3590266b475c'),
	 ('4aab1a48-d3c0-409b-bd16-0f393de85464','loosahatchie-river','Loosahatchie River',ST_GeomFromText('POLYGON ((530000 1410000, 624000 1410000, 624000 1358000, 530000 1358000, 530000 1410000))',5070),'8fc88b15-9cd4-4e86-8b8c-6d956926010b'),
	 ('4b9922fe-ac30-4a35-8ef1-0741b8b41128','san-diego-creek','San Diego Creek',ST_GeomFromText('POLYGON ((-266000 552000, -194000 552000, -194000 514000, -266000 514000, -266000 552000))',5070),'4f4f6899-cac1-402f-adee-8109d5bc5db3'),
	 ('4c43255a-3af2-4cb0-94f8-4d2b82b31055','licking-river','Licking River',ST_GeomFromText('POLYGON ((968000 1850000, 1150000 1850000, 1150000 1678000, 968000 1678000, 968000 1850000))',5070),'b952664c-4b11-4d85-89fa-a2cc405b1131'),
	 ('4d3083d1-101c-4b76-9311-1154917ffbf1','twelvepole-river','Twelvepole River',ST_GeomFromText('POLYGON ((1152000 1796000, 1212000 1796000, 1212000 1728000, 1152000 1728000, 1152000 1796000))',5070),'788cc853-235a-4e43-a136-b1f190a6a656'),
	 ('4f8dc36b-f813-4643-8e4a-0da780ff1ea8','potomac-river','Potomac River',ST_GeomFromText('POLYGON ((1396000 2064000, 1636000 2064000, 1636000 1776000, 1396000 1776000, 1396000 2064000))',5070),'7d7e962d-e554-48f0-8f82-b762a31441a6'),
	 ('5024720e-02f6-4577-a09c-ff1ff5a28223','hocking-river','Hocking River',ST_GeomFromText('POLYGON ((1112000 1960000, 1220000 1960000, 1220000 1878000, 1112000 1878000, 1112000 1960000))',5070),'788cc853-235a-4e43-a136-b1f190a6a656'),
	 ('50372dbc-f254-4584-8345-1c3613d2a102','guyandotte-river','Guyandotte River',ST_GeomFromText('POLYGON ((1166000 1814000, 1298000 1814000, 1298000 1692000, 1166000 1692000, 1166000 1814000))',5070),'788cc853-235a-4e43-a136-b1f190a6a656'),
	 ('514fcc89-359b-4d8c-ad92-6a968d1188e5','district-cemvs','District CEMVS',ST_GeomFromText('POLYGON ((280000 1944000, 670000 1944000, 670000 1450000, 280000 1450000, 280000 1944000))',5070),'0088df5f-ec58-4654-9b71-3590266b475c'),
	 ('51f3f619-ce6e-4255-9464-7a498ac1b870','nf-clearwater-river','NF Clearwater River',ST_GeomFromText('POLYGON ((-1616000 2844000, -1394000 2844000, -1394000 2636000, -1616000 2636000, -1616000 2844000))',5070),'834ea54d-2454-425f-b443-50ba4ab46e28'),
	 ('523ed612-a97c-4943-9303-938b62b627f6','pecos-river','Pecos River',ST_GeomFromText('POLYGON ((-916000 1486000, -490000 1486000, -490000 744000, -916000 744000, -916000 1486000))',5070),'a9929dc4-7d7c-4ddb-b727-d752137ffc10'),
	 ('538c3ca9-f29a-4789-b43e-bf1bb73a3c78','upper-susquehanna-river','Upper Susquehanna River',ST_GeomFromText('POLYGON ((1558000 2410000, 1740000 2410000, 1740000 2140000, 1558000 2140000, 1558000 2410000))',5070),'7d7e962d-e554-48f0-8f82-b762a31441a6'),
	 ('5580c215-3b32-414c-809c-e43277867729','castor-river-and-headwaters','Castor River and Headwaters',ST_GeomFromText('POLYGON ((514000 1596000, 558000 1596000, 558000 1548000, 514000 1548000, 514000 1596000))',5070),'8fc88b15-9cd4-4e86-8b8c-6d956926010b'),
	 ('4570d57c-dddd-49cb-bbc6-08059911be0d','oahe-to-fort-randall','Oahe to Fort Randall',ST_GeomFromText('POLYGON ((-644000 2452000, -184000 2452000, -184000 2188000, -644000 2188000, -644000 2452000))',5070),'90173658-2de9-4329-926d-176c1b29089a'),
	 ('3e93f77a-6982-42cb-9da2-26b1d358d257','kootenai-river','Kootenai River',ST_GeomFromText('POLYGON ((-1608000 3302000, -1346000 3302000, -1346000 2908000, -1608000 2908000, -1608000 3302000))',5070),'c88758e9-4575-44b0-9d38-b6c0ee909061'),
	 ('55838c5a-14d3-4fec-8d94-f8b13a847257','great-dismal-swamp','Great Dismal Swamp',ST_GeomFromText('POLYGON ((1694000 1708000, 1740000 1708000, 1740000 1664000, 1694000 1664000, 1694000 1708000))',5070),'7fd53614-f484-4dfd-8fc4-d11b11fb071c'),
	 ('55bd2fe3-39cf-4972-96c1-3781631da1fe','rio-grande','Rio Grande',ST_GeomFromText('POLYGON ((-1332000 1766000, -482000 1766000, -482000 560000, -1332000 560000, -1332000 1766000))',5070),'a9929dc4-7d7c-4ddb-b727-d752137ffc10'),
	 ('56a44c47-6645-413c-bc02-daf56b42b526','russian-river','Russian River',ST_GeomFromText('POLYGON ((-2320000 2154000, -2258000 2154000, -2258000 2014000, -2320000 2014000, -2320000 2154000))',5070),'76bb611e-3fbf-4779-b251-203de3502670'),
	 ('571ecb91-c212-4149-9198-1139c01a1cc4','white-river','White River',ST_GeomFromText('POLYGON ((334000 1378000, 498000 1378000, 498000 1214000, 334000 1214000, 334000 1378000))',5070),'8fc88b15-9cd4-4e86-8b8c-6d956926010b'),
	 ('5758d0dc-c8bf-4e37-a5e7-44ff3f4b8677','scioto-river','Scioto River',ST_GeomFromText('POLYGON ((1004000 2056000, 1154000 2056000, 1154000 1810000, 1004000 1810000, 1004000 2056000))',5070),'788cc853-235a-4e43-a136-b1f190a6a656'),
	 ('58988034-f0f6-4af3-ad70-382f28eea191','cape-fear-river','Cape Fear River',ST_GeomFromText('POLYGON ((1408000 1608000, 1674000 1608000, 1674000 1324000, 1408000 1324000, 1408000 1608000))',5070),'098c898f-7f0f-44e8-b2c1-329d7dd50166'),
	 ('58d9a67c-a1b4-4a9c-9364-9edb4d0af1c2','little-river','Little River',ST_GeomFromText('POLYGON ((122000 1276000, 208000 1276000, 208000 1164000, 122000 1164000, 122000 1276000))',5070),'60754640-fef3-429b-b2f4-efdcf3b61e55'),
	 ('59e880ca-f242-4f9a-b1f8-06424f8bb23f','trinity-river','Trinity River',ST_GeomFromText('POLYGON ((92000 830000, 146000 830000, 146000 738000, 92000 738000, 92000 830000))',5070),'4f4f6899-cac1-402f-adee-8109d5bc5db3'),
	 ('5bb72f21-d26c-4163-92c0-533efdd97c70','neosho-river','Neosho River',ST_GeomFromText('POLYGON ((-128000 1766000, 218000 1766000, 218000 1410000, -128000 1410000, -128000 1766000))',5070),'26e6c300-480b-4e22-afae-7cc27dd9b116'),
	 ('5bff9e44-826b-4e40-a216-a7e931b94b63','washita-river','Washita River',ST_GeomFromText('POLYGON ((-424000 1438000, -36000 1438000, -36000 1196000, -424000 1196000, -424000 1438000))',5070),'26e6c300-480b-4e22-afae-7cc27dd9b116'),
	 ('5c0c5fd1-3c53-4c83-ab8a-b4eb1fedab68','mojave-river','Mojave River',ST_GeomFromText('POLYGON ((-1968000 1570000, -1732000 1570000, -1732000 1444000, -1968000 1444000, -1968000 1570000))',5070),'89a1fe0c-03f3-47cf-8ee1-cd3de2e1ba7b'),
	 ('5c7d02c9-0403-4f3d-be76-85b5f21de64d','provo-river','Provo River',ST_GeomFromText('POLYGON ((-1326000 2074000, -1238000 2074000, -1238000 2016000, -1326000 2016000, -1326000 2074000))',5070),'df64a2de-91a2-4e6c-85c9-53d3d03f6794'),
	 ('5dd34237-def2-4b43-b54d-896449d43707','horn-lake-creek','Horn Lake Creek',ST_GeomFromText('POLYGON ((514000 1356000, 554000 1356000, 554000 1328000, 514000 1328000, 514000 1356000))',5070),'8fc88b15-9cd4-4e86-8b8c-6d956926010b'),
	 ('5e343967-51bf-401f-941e-91e10f69677e','willamette','Willamette',ST_GeomFromText('POLYGON ((-2170000 2846000, -1990000 2846000, -1990000 2550000, -2170000 2550000, -2170000 2846000))',5070),'cf0e2fde-9156-4a96-a8bc-32640cb0043d'),
	 ('5ebdb9a2-2bb4-443c-bf08-d05637121954','wolf-river','Wolf River',ST_GeomFromText('POLYGON ((532000 1378000, 640000 1378000, 640000 1324000, 532000 1324000, 532000 1378000))',5070),'8fc88b15-9cd4-4e86-8b8c-6d956926010b'),
	 ('609b5b69-4c51-4ed7-be2e-6284bcec4083','kissimmee-river','Kissimmee River',ST_GeomFromText('POLYGON ((1392000 726000, 1508000 726000, 1508000 558000, 1392000 558000, 1392000 726000))',5070),'4142c26c-0407-41ad-b660-8657ddb2be69'),
	 ('6123290b-756b-49e5-8097-912bd80296ea','boise-river','Boise River',ST_GeomFromText('POLYGON ((-1676000 2508000, -1482000 2508000, -1482000 2402000, -1676000 2402000, -1676000 2508000))',5070),'834ea54d-2454-425f-b443-50ba4ab46e28'),
	 ('624df329-a604-4a1f-a009-9c9fb035c587','mississippi-river-2','Mississippi River',ST_GeomFromText('POLYGON ((444000 1604000, 626000 1604000, 626000 1192000, 444000 1192000, 444000 1604000))',5070),'8fc88b15-9cd4-4e86-8b8c-6d956926010b'),
	 ('64b7be1b-5016-4337-8d74-462945b4333a','des-moines-river','Des Moines River',ST_GeomFromText('POLYGON ((-14000 2368000, 390000 2368000, 390000 1932000, -14000 1932000, -14000 2368000))',5070),'b9c56905-9dad-4418-9654-d1fcd9b3a57f'),
	 ('65a93467-c9b4-4166-acb6-58e8ec06ed3b','kanawha-river','Kanawha River',ST_GeomFromText('POLYGON ((1182000 1870000, 1410000 1870000, 1410000 1544000, 1182000 1544000, 1182000 1870000))',5070),'788cc853-235a-4e43-a136-b1f190a6a656'),
	 ('65c40945-527e-43c4-917b-bd0593db782b','gila-river','Gila River',ST_GeomFromText('POLYGON ((-1726000 1566000, -1076000 1566000, -1076000 970000, -1726000 970000, -1726000 1566000))',5070),'89a1fe0c-03f3-47cf-8ee1-cd3de2e1ba7b'),
	 ('65f92ccc-ccb8-400f-a56c-301f66d9a315','east-branch-river','East Branch River',ST_GeomFromText('POLYGON ((1850000 2334000, 1886000 2334000, 1886000 2286000, 1850000 2286000, 1850000 2334000))',5070),'64fb2c2f-e59a-44cc-a54d-22e8d7c909a0'),
	 ('686026c0-bc68-45e8-95c6-1ccb0aec6682','neuse-river','Neuse River',ST_GeomFromText('POLYGON ((1484000 1624000, 1664000 1624000, 1664000 1494000, 1484000 1494000, 1484000 1624000))',5070),'098c898f-7f0f-44e8-b2c1-329d7dd50166'),
	 ('6d134b7c-5312-43bb-864e-737553cc5081','pend-oreille','Pend Oreille',ST_GeomFromText('POLYGON ((-1604000 3112000, -1238000 3112000, -1238000 2632000, -1604000 2632000, -1604000 3112000))',5070),'cf0e2fde-9156-4a96-a8bc-32640cb0043d'),
	 ('6d187828-2182-48e9-99d5-c2fdaa468ded','whitewater-river','Whitewater River',ST_GeomFromText('POLYGON ((900000 1958000, 968000 1958000, 968000 1844000, 900000 1844000, 900000 1958000))',5070),'b952664c-4b11-4d85-89fa-a2cc405b1131'),
	 ('6dd5b1af-cb1e-492e-a7e1-2efce9628aff','yazoo-river','Yazoo River',ST_GeomFromText('POLYGON ((440000 1350000, 656000 1350000, 656000 1036000, 440000 1036000, 440000 1350000))',5070),'d02f876f-eb00-425b-aeca-09fa105d5bc2'),
	 ('6df75b34-e8fe-43df-a148-36a54181b791','red-river','Red River',ST_GeomFromText('POLYGON ((-708000 1412000, 206000 1412000, 206000 1144000, -708000 1144000, -708000 1412000))',5070),'26e6c300-480b-4e22-afae-7cc27dd9b116'),
	 ('724b7228-6174-42c3-b455-a6e4b09f65ee','nws-rfc---southeast','NWS RFC - Southeast',ST_GeomFromText('POLYGON ((456000 2058000, 2112000 2058000, 2112000 182000, 456000 182000, 456000 2058000))',5070),'e303450f-af6a-4272-a262-fdb94f8e3e86'),
	 ('76122e85-f95b-4332-b500-18090f4a1543','umpqua-river','Umpqua River',ST_GeomFromText('POLYGON ((-2240000 2660000, -2068000 2660000, -2068000 2496000, -2240000 2496000, -2240000 2660000))',5070),'c18588b6-25ab-42c9-b31a-a33c585d0b49'),
	 ('77f3cc8d-eac6-4313-ba41-108e6e09059f','canadian-river','Canadian River',ST_GeomFromText('POLYGON ((-858000 1604000, -626000 1604000, -626000 1330000, -858000 1330000, -858000 1604000))',5070),'a9929dc4-7d7c-4ddb-b727-d752137ffc10'),
	 ('78cbbef1-d43e-43d7-b49f-e4d985b2e209','middle-snake-river','Middle Snake River',ST_GeomFromText('POLYGON ((-1802000 2656000, -1482000 2656000, -1482000 2186000, -1802000 2186000, -1802000 2656000))',5070),'834ea54d-2454-425f-b443-50ba4ab46e28'),
	 ('79d75b8a-9dee-4cd2-a85b-f4244bbeeb8a','st-francis-basin','St Francis Basin',ST_GeomFromText('POLYGON ((436000 1602000, 612000 1602000, 612000 1292000, 436000 1292000, 436000 1602000))',5070),'8fc88b15-9cd4-4e86-8b8c-6d956926010b'),
	 ('7a5adcc3-254a-40a3-a38f-d6d66a8c8306','green-river-1','Green River',ST_GeomFromText('POLYGON ((720000 1694000, 998000 1694000, 998000 1528000, 720000 1528000, 720000 1694000))',5070),'b952664c-4b11-4d85-89fa-a2cc405b1131'),
	 ('7a7939ca-de80-40b2-9e0a-96f01f98d9ff','lake-winnebago','Lake Winnebago',ST_GeomFromText('POLYGON ((500000 2556000, 656000 2556000, 656000 2294000, 500000 2294000, 500000 2556000))',5070),'586ac79a-083e-4c8c-8438-9585a88a4b3d'),
	 ('7b07bcb2-54df-439f-b207-0c2179194f65','blackstone-river','Blackstone River',ST_GeomFromText('POLYGON ((1946000 2408000, 2012000 2408000, 2012000 2344000, 1946000 2344000, 1946000 2408000))',5070),'64fb2c2f-e59a-44cc-a54d-22e8d7c909a0'),
	 ('7b550f3a-91c3-4136-9595-d6e5acf1b7fa','san-joaquin-river','San Joaquin River',ST_GeomFromText('POLYGON ((-2238000 2030000, -1968000 2030000, -1968000 1758000, -2238000 1758000, -2238000 2030000))',5070),'df64a2de-91a2-4e6c-85c9-53d3d03f6794'),
	 ('7b6320f8-c5e4-4306-9c9e-41752855da1d','missouri-river','Missouri River',ST_GeomFromText('POLYGON ((-1394000 3044000, 510000 3044000, 510000 1552000, -1394000 1552000, -1394000 3044000))',5070),'90173658-2de9-4329-926d-176c1b29089a'),
	 ('7bfb20a3-f603-4627-9930-36c09e8bcad3','mississippi-river-3','Mississippi River',ST_GeomFromText('POLYGON ((162000 2338000, 636000 2338000, 636000 1810000, 162000 1810000, 162000 2338000))',5070),'b9c56905-9dad-4418-9654-d1fcd9b3a57f'),
	 ('7c6dd902-fbc5-43e4-9bbf-351963f5723d','muskingum-river','Muskingum River',ST_GeomFromText('POLYGON ((1098000 2110000, 1268000 2110000, 1268000 1904000, 1098000 1904000, 1098000 2110000))',5070),'788cc853-235a-4e43-a136-b1f190a6a656'),
	 ('7e97fc93-57e0-4e4c-aa5e-3475c644a0fc','arkansas-river','Arkansas River',ST_GeomFromText('POLYGON ((140000 1432000, 460000 1432000, 460000 1196000, 140000 1196000, 140000 1432000))',5070),'60754640-fef3-429b-b2f4-efdcf3b61e55'),
	 ('801b909e-935b-4367-a564-7b000c65dd44','passaic-river-1','Passaic River',ST_GeomFromText('POLYGON ((1766000 2252000, 1832000 2252000, 1832000 2154000, 1766000 2154000, 1766000 2252000))',5070),'ede616b6-5ab7-42c6-9489-7c09bfb6a54b'),
	 ('80292ae1-5bbb-4048-8f3a-193bdeaee71f','lower-snake-river','Lower Snake River',ST_GeomFromText('POLYGON ((-1772000 2928000, -1336000 2928000, -1336000 2454000, -1772000 2454000, -1772000 2928000))',5070),'834ea54d-2454-425f-b443-50ba4ab46e28'),
	 ('81e4879f-3c8e-4aa6-b96e-0393898f4ee8','willow-creek','Willow Creek',ST_GeomFromText('POLYGON ((-1292000 2404000, -1228000 2404000, -1228000 2308000, -1292000 2308000, -1292000 2404000))',5070),'834ea54d-2454-425f-b443-50ba4ab46e28'),
	 ('8397f01c-2ed5-4519-8a86-2ae97ec4d630','middle-columbia','Middle Columbia',ST_GeomFromText('POLYGON ((-1880000 3272000, -1562000 3272000, -1562000 2814000, -1880000 2814000, -1880000 3272000))',5070),'cf0e2fde-9156-4a96-a8bc-32640cb0043d'),
	 ('8441e64e-fda6-4c35-a0c0-9cf5a8a725d9','iowa-river','Iowa River',ST_GeomFromText('POLYGON ((168000 2338000, 444000 2338000, 444000 2006000, 168000 2006000, 168000 2338000))',5070),'b9c56905-9dad-4418-9654-d1fcd9b3a57f'),
	 ('84f2c025-8bea-4763-b85b-c8caf975d1d5','mainstem-columbia','Mainstem Columbia',ST_GeomFromText('POLYGON ((-2006000 2872000, -1698000 2872000, -1698000 2548000, -2006000 2548000, -2006000 2872000))',5070),'cf0e2fde-9156-4a96-a8bc-32640cb0043d'),
	 ('85a48fd2-f125-4e94-b1f8-234dc4450bbc','cuivre-river','Cuivre River',ST_GeomFromText('POLYGON ((356000 1828000, 462000 1828000, 462000 1758000, 356000 1758000, 356000 1828000))',5070),'0088df5f-ec58-4654-9b71-3590266b475c'),
	 ('85fe599a-fcac-4f2b-8e7e-1d5cbe1e4f93','parleys-canyon-creek','Parleys Canyon Creek',ST_GeomFromText('POLYGON ((-1368000 2110000, -1268000 2110000, -1268000 1946000, -1368000 1946000, -1368000 2110000))',5070),'df64a2de-91a2-4e6c-85c9-53d3d03f6794'),
	 ('8668a317-d4cd-4412-b8b2-0b50207db836','pearl-river','Pearl River',ST_GeomFromText('POLYGON ((504000 1174000, 676000 1174000, 676000 802000, 504000 802000, 504000 1174000))',5070),'d02f876f-eb00-425b-aeca-09fa105d5bc2'),
	 ('874c4639-73ae-47e3-a257-d1a39449e79f','merrimack-river','Merrimack River',ST_GeomFromText('POLYGON ((1892000 2612000, 2030000 2612000, 2030000 2384000, 1892000 2384000, 1892000 2612000))',5070),'64fb2c2f-e59a-44cc-a54d-22e8d7c909a0'),
	 ('8966ac1d-6e9d-477f-a898-84e9a0336e6b','smith-river','Smith River',ST_GeomFromText('POLYGON ((1362000 1668000, 1542000 1668000, 1542000 1566000, 1362000 1566000, 1362000 1668000))',5070),'098c898f-7f0f-44e8-b2c1-329d7dd50166'),
	 ('8acff577-28d7-4939-be38-4c1bd7b5c740','guadalupe-river','Guadalupe River',ST_GeomFromText('POLYGON ((-360000 810000, -100000 810000, -100000 658000, -360000 658000, -360000 810000))',5070),'a222e733-2fa7-4cd8-b3a6-065956e693f0'),
	 ('8b842c27-4835-483c-894e-bc48c426ef36','yakima','Yakima',ST_GeomFromText('POLYGON ((-1938000 2986000, -1776000 2986000, -1776000 2784000, -1938000 2784000, -1938000 2986000))',5070),'cf0e2fde-9156-4a96-a8bc-32640cb0043d'),
	 ('8bd62150-d090-415a-bc01-33416705e19c','puyallup-river','Puyallup River',ST_GeomFromText('POLYGON ((-1992000 2980000, -1908000 2980000, -1908000 2908000, -1992000 2908000, -1992000 2980000))',5070),'c88758e9-4575-44b0-9d38-b6c0ee909061'),
	 ('8e18c5ef-6f8f-42d3-8048-1ed6d7da98f7','arkansas-river-1','Arkansas River',ST_GeomFromText('POLYGON ((-912000 1872000, -516000 1872000, -516000 1564000, -912000 1564000, -912000 1872000))',5070),'a9929dc4-7d7c-4ddb-b727-d752137ffc10'),
	 ('8ea237ca-7705-409c-9ee8-c4d987072c85','mvk-red-river','MVK Red River',ST_GeomFromText('POLYGON ((156000 1202000, 422000 1202000, 422000 888000, 156000 888000, 156000 1202000))',5070),'d02f876f-eb00-425b-aeca-09fa105d5bc2'),
	 ('91f92bef-817b-4663-a8f3-84dd964cf4a0','lower-colorado-river','Lower Colorado River',ST_GeomFromText('POLYGON ((-76000 746000, 10000 746000, 10000 608000, -76000 608000, -76000 746000))',5070),'4f4f6899-cac1-402f-adee-8109d5bc5db3'),
	 ('92ed20bc-c948-4e3d-8d7f-fa57d065ea0a','roanoke-river','Roanoke River',ST_GeomFromText('POLYGON ((1358000 1740000, 1702000 1740000, 1702000 1568000, 1358000 1568000, 1358000 1740000))',5070),'098c898f-7f0f-44e8-b2c1-329d7dd50166'),
	 ('9484f2ab-b465-40b4-879d-68f6dd02e350','salt-river','Salt River',ST_GeomFromText('POLYGON ((280000 1944000, 426000 1944000, 426000 1780000, 280000 1780000, 280000 1944000))',5070),'0088df5f-ec58-4654-9b71-3590266b475c'),
	 ('94e7713a-ccd6-432d-b2f0-972422511171','genesee-river','Genesee River',ST_GeomFromText('POLYGON ((1428000 2400000, 1508000 2400000, 1508000 2230000, 1428000 2230000, 1428000 2400000))',5070),'60c46088-9c98-4927-991d-0bd126bbb62e'),
	 ('952b3a65-24f0-4331-82ac-d7640c034c06','schuylkill-river','Schuylkill River',ST_GeomFromText('POLYGON ((1628000 2168000, 1756000 2168000, 1756000 2060000, 1628000 2060000, 1628000 2168000))',5070),'6e3c2e48-a15a-4892-ba91-caab86499abc'),
	 ('9539aa91-7c1d-4bf0-939c-7915667b36bc','weber-river','Weber River',ST_GeomFromText('POLYGON ((-1352000 2164000, -1236000 2164000, -1236000 2050000, -1352000 2050000, -1352000 2164000))',5070),'df64a2de-91a2-4e6c-85c9-53d3d03f6794'),
	 ('965e523a-08b4-4567-8b9f-4ac8882fb0e1','alameda-creek','Alameda Creek',ST_GeomFromText('POLYGON ((-2240000 1938000, -2198000 1938000, -2198000 1876000, -2240000 1876000, -2240000 1938000))',5070),'76bb611e-3fbf-4779-b251-203de3502670'),
	 ('96789834-96e1-4c5a-9364-f8c8bdfe0a27','acushnet-river','Acushnet River',ST_GeomFromText('POLYGON ((2038000 2366000, 2062000 2366000, 2062000 2324000, 2038000 2324000, 2038000 2366000))',5070),'64fb2c2f-e59a-44cc-a54d-22e8d7c909a0'),
	 ('97a5c6dc-e7cd-4e99-9344-4cf7dde96dc1','spokane','Spokane',ST_GeomFromText('POLYGON ((-1670000 2984000, -1446000 2984000, -1446000 2808000, -1670000 2808000, -1670000 2984000))',5070),'cf0e2fde-9156-4a96-a8bc-32640cb0043d'),
	 ('9c3323d6-7cd0-4845-ad63-14424cf25895','verdigris-river','Verdigris River',ST_GeomFromText('POLYGON ((-64000 1700000, 74000 1700000, 74000 1412000, -64000 1412000, -64000 1700000))',5070),'26e6c300-480b-4e22-afae-7cc27dd9b116'),
	 ('9d0be099-6751-49d9-8ced-9c4b93d0bd2c','mill-creek-1','Mill Creek',ST_GeomFromText('POLYGON ((968000 1884000, 998000 1884000, 998000 1840000, 968000 1840000, 968000 1884000))',5070),'b952664c-4b11-4d85-89fa-a2cc405b1131'),
	 ('a203e1f0-1654-456b-95c6-1c00f4298fdb','upper-snake','Upper Snake',ST_GeomFromText('POLYGON ((-1588000 2516000, -1100000 2516000, -1100000 2200000, -1588000 2200000, -1588000 2516000))',5070),'cf0e2fde-9156-4a96-a8bc-32640cb0043d'),
	 ('a3139295-0c31-4d0d-9e7a-de99e700e7bb','trinity-river-1','Trinity River',ST_GeomFromText('POLYGON ((-258000 1192000, 134000 1192000, 134000 812000, -258000 812000, -258000 1192000))',5070),'a222e733-2fa7-4cd8-b3a6-065956e693f0'),
	 ('a55cfc71-ce33-435d-9606-229a95fe4083','pascagoula-river','Pascagoula River',ST_GeomFromText('POLYGON ((574000 1104000, 724000 1104000, 724000 860000, 574000 860000, 574000 1104000))',5070),'eb545b18-5498-43c8-8652-f73e16446cc0'),
	 ('a6513264-cd38-4b32-a55f-89a4f0e4d7bb','kiamichi-river','Kiamichi River',ST_GeomFromText('POLYGON ((12000 1312000, 146000 1312000, 146000 1200000, 12000 1200000, 12000 1312000))',5070),'26e6c300-480b-4e22-afae-7cc27dd9b116'),
	 ('a7e73cb4-e74f-414f-a8bf-6cbb953ab1c9','canadian-river-1','Canadian River',ST_GeomFromText('POLYGON ((-730000 1572000, 92000 1572000, 92000 1278000, -730000 1278000, -730000 1572000))',5070),'26e6c300-480b-4e22-afae-7cc27dd9b116'),
	 ('a9a581e7-37f1-40ef-a80e-3a6cd394398c','illinois-river','Illinois River',ST_GeomFromText('POLYGON ((400000 1910000, 552000 1910000, 552000 1772000, 400000 1772000, 400000 1910000))',5070),'0088df5f-ec58-4654-9b71-3590266b475c'),
	 ('a9e18c78-094c-4cc9-830c-3d146931a2c8','black-creek','Black Creek',ST_GeomFromText('POLYGON ((510000 1164000, 572000 1164000, 572000 1094000, 510000 1094000, 510000 1164000))',5070),'d02f876f-eb00-425b-aeca-09fa105d5bc2'),
	 ('abd7e8c2-69bb-4bf2-b309-478307ab523d','little-wood-river','Little Wood River',ST_GeomFromText('POLYGON ((-1520000 2450000, -1408000 2450000, -1408000 2334000, -1520000 2334000, -1520000 2450000))',5070),'834ea54d-2454-425f-b443-50ba4ab46e28'),
	 ('acd99672-26c8-48f0-8805-bb4d7a47d287','ohio-river-1','Ohio River',ST_GeomFromText('POLYGON ((584000 2004000, 1028000 2004000, 1028000 1566000, 584000 1566000, 584000 2004000))',5070),'b952664c-4b11-4d85-89fa-a2cc405b1131'),
	 ('ad30f178-afc3-43b9-ba92-7bd139581217','red-river-north','Red River North',ST_GeomFromText('POLYGON ((-356000 2950000, 150000 2950000, 150000 2494000, -356000 2494000, -356000 2950000))',5070),'33f03e9a-711b-41e7-9bdd-66152b69128d'),
	 ('ad4c7952-b395-449a-9ac1-182bdd6ead5d','district-cenae','District CENAE',ST_GeomFromText('POLYGON ((1800000 3080000, 2284000 3080000, 2284000 2180000, 1800000 2180000, 1800000 3080000))',5070),'64fb2c2f-e59a-44cc-a54d-22e8d7c909a0'),
	 ('ad7e4854-0997-4abd-859b-ca2fa7a21380','main-stem-susquehanna-river','Main Stem Susquehanna River',ST_GeomFromText('POLYGON ((1512000 2162000, 1696000 2162000, 1696000 2004000, 1512000 2004000, 1512000 2162000))',5070),'7d7e962d-e554-48f0-8f82-b762a31441a6'),
	 ('b08b981b-9650-4735-b5b6-fba8db32f5b1','pend-oreille-river','Pend Oreille River',ST_GeomFromText('POLYGON ((-1608000 3118000, -1234000 3118000, -1234000 2630000, -1608000 2630000, -1608000 3118000))',5070),'c88758e9-4575-44b0-9d38-b6c0ee909061'),
	 ('b0be5646-59d7-4281-a91b-919264e380be','columbia-river-1','Columbia River',ST_GeomFromText('POLYGON ((-1798000 2872000, -1678000 2872000, -1678000 2746000, -1798000 2746000, -1798000 2872000))',5070),'834ea54d-2454-425f-b443-50ba4ab46e28'),
	 ('b30c6162-3801-4014-b59a-3224c5a0ab10','fort-peck-to-garrison','Fort Peck to Garrison',ST_GeomFromText('POLYGON ((-1294000 3042000, -372000 3042000, -372000 2228000, -1294000 2228000, -1294000 3042000))',5070),'1f579664-d1db-4ee9-897e-47c16dc55012'),
	 ('b364838d-dfd1-4acf-8719-f7daccd5cfcf','great-miami-river','Great Miami River',ST_GeomFromText('POLYGON ((930000 2028000, 1056000 2028000, 1056000 1838000, 930000 1838000, 930000 2028000))',5070),'b952664c-4b11-4d85-89fa-a2cc405b1131'),
	 ('b40c219b-188d-4a3b-ab41-0087ea7dca5c','white-river-tributary','White River Tributary',ST_GeomFromText('POLYGON ((406000 1528000, 520000 1528000, 520000 1298000, 406000 1298000, 406000 1528000))',5070),'8fc88b15-9cd4-4e86-8b8c-6d956926010b'),
	 ('b9ac7096-ff2d-41b4-9ac8-8ab5f76ab2b7','sulphur-river','Sulphur River',ST_GeomFromText('POLYGON ((-28000 1188000, 208000 1188000, 208000 1044000, -28000 1044000, -28000 1188000))',5070),'a222e733-2fa7-4cd8-b3a6-065956e693f0'),
	 ('ba08540e-fdf2-44ea-b734-b63e56e522f2','meadow-valley-river','Meadow Valley River',ST_GeomFromText('POLYGON ((-1656000 1862000, -1554000 1862000, -1554000 1668000, -1656000 1668000, -1656000 1862000))',5070),'89a1fe0c-03f3-47cf-8ee1-cd3de2e1ba7b'),
	 ('ba17efef-1edc-4c1e-8b70-8c2d27861ee1','chena-river','Chena River',ST_GeomFromText('POLYGON ((-2830000 5324000, -2634000 5324000, -2634000 5228000, -2830000 5228000, -2830000 5324000))',5070),'a0baec43-2817-4161-b654-c3c513b5276b'),
	 ('ba367a57-288d-43f9-ae12-409afb4cb827','illinois-river-1','Illinois River',ST_GeomFromText('POLYGON ((396000 2276000, 842000 2276000, 842000 1824000, 396000 1824000, 396000 2276000))',5070),'b9c56905-9dad-4418-9654-d1fcd9b3a57f'),
	 ('ba66c452-2464-4415-a20a-6c0315b13391','kentucky-river','Kentucky River',ST_GeomFromText('POLYGON ((924000 1818000, 1176000 1818000, 1176000 1606000, 924000 1606000, 924000 1818000))',5070),'b952664c-4b11-4d85-89fa-a2cc405b1131'),
	 ('bcab224b-bbc9-4896-8edc-acc093e5133e','brazos-river','Brazos River',ST_GeomFromText('POLYGON ((-724000 1324000, 14000 1324000, 14000 774000, -724000 774000, -724000 1324000))',5070),'a222e733-2fa7-4cd8-b3a6-065956e693f0'),
	 ('c0828c98-0193-4b15-87fd-37a72f7345a8','santa-ana-river','Santa Ana River',ST_GeomFromText('POLYGON ((-2022000 1486000, -1874000 1486000, -1874000 1364000, -2022000 1364000, -2022000 1486000))',5070),'89a1fe0c-03f3-47cf-8ee1-cd3de2e1ba7b'),
	 ('c0eddfc8-2a0a-4187-bae3-304ed2ce4f31','lower-snake','Lower Snake',ST_GeomFromText('POLYGON ((-1794000 2924000, -1340000 2924000, -1340000 2456000, -1794000 2456000, -1794000 2924000))',5070),'cf0e2fde-9156-4a96-a8bc-32640cb0043d'),
	 ('c1267878-cd1c-4a41-a93f-97eef1b8964e','skagit-river','Skagit River',ST_GeomFromText('POLYGON ((-1986000 3176000, -1804000 3176000, -1804000 3020000, -1986000 3020000, -1986000 3176000))',5070),'c88758e9-4575-44b0-9d38-b6c0ee909061'),
	 ('c16af9a3-ce7c-410b-a9d6-5317a1f3fd08','middle-snake','Middle Snake',ST_GeomFromText('POLYGON ((-1812000 2664000, -1486000 2664000, -1486000 2188000, -1812000 2188000, -1812000 2664000))',5070),'cf0e2fde-9156-4a96-a8bc-32640cb0043d'),
	 ('c1b7f4ea-a8ac-40e8-8431-409420a14be0','truckee-river','Truckee River',ST_GeomFromText('POLYGON ((-2068000 2200000, -1872000 2200000, -1872000 1996000, -2068000 1996000, -2068000 2200000))',5070),'df64a2de-91a2-4e6c-85c9-53d3d03f6794'),
	 ('c2015f99-c99d-407b-bbbd-c2d79a404806','allegheny-river','Allegheny River',ST_GeomFromText('POLYGON ((1280000 2298000, 1494000 2298000, 1494000 2002000, 1280000 2002000, 1280000 2298000))',5070),'e7c9cfe8-99eb-4845-a058-46e53a75b28b'),
	 ('c26daa2f-431e-4351-b45e-3907df68453c','chemung-river','Chemung River',ST_GeomFromText('POLYGON ((1466000 2336000, 1598000 2336000, 1598000 2218000, 1466000 2218000, 1466000 2336000))',5070),'7d7e962d-e554-48f0-8f82-b762a31441a6'),
	 ('c3082967-c74e-4931-9da6-118d761b43b5','buffalo-bayou-river','Buffalo Bayou River',ST_GeomFromText('POLYGON ((-2000 776000, 106000 776000, 106000 718000, -2000 718000, -2000 776000))',5070),'4f4f6899-cac1-402f-adee-8109d5bc5db3'),
	 ('c339ed05-58c5-4e2b-83eb-e201832fdbfc','little-wabash-river','Little Wabash River',ST_GeomFromText('POLYGON ((608000 1860000, 698000 1860000, 698000 1674000, 608000 1674000, 608000 1860000))',5070),'b952664c-4b11-4d85-89fa-a2cc405b1131'),
	 ('c54eab5b-1020-476b-a5f8-56d77802d9bf','tennessee-river','Tennessee River',ST_GeomFromText('POLYGON ((640000 1678000, 1300000 1678000, 1300000 1268000, 640000 1268000, 640000 1678000))',5070),'4ffaa895-0f05-4b59-8d12-86c901e2f229'),
	 ('c572ed70-d401-4a97-aea6-cb3fe2b77e41','savannah-river-basin','Savannah River Basin',ST_GeomFromText('POLYGON ((1110000 1432000, 1432000 1432000, 1432000 1094000, 1110000 1094000, 1110000 1432000))',5070),'90b958ea-0076-4925-87d8-670eb7da5551'),
	 ('c5b59e1a-ccc3-46b8-846f-82e80823c581','caloosahatchee-river','Caloosahatchee River',ST_GeomFromText('POLYGON ((1394000 552000, 1530000 552000, 1530000 480000, 1394000 480000, 1394000 552000))',5070),'4142c26c-0407-41ad-b660-8657ddb2be69'),
	 ('c785f4de-ab17-444b-b6e6-6f1ad16676e8','cumberland-basin-river','Cumberland Basin River',ST_GeomFromText('POLYGON ((662000 1678000, 1172000 1678000, 1172000 1408000, 662000 1408000, 662000 1678000))',5070),'4ffaa895-0f05-4b59-8d12-86c901e2f229'),	 																																	
	 ('feda585b-1ba0-4b19-92ed-7195154b8052', 'tennessee-cumberland-river', 'Tennessee & Cumberland River', ST_GeomFromText('POLYGON ((642000 1682000, 1300000 1682000, 1300000 1258000, 642000 1258000, 642000 1682000))',5070), '4ffaa895-0f05-4b59-8d12-86c901e2f229'),
	 ('c88676cc-b1c0-4d2c-9a88-ca86956f281b','alabama-coosa-tallapoosa-rivers','Alabama Coosa Tallapoosa Rivers',ST_GeomFromText('POLYGON ((760000 1408000, 1098000 1408000, 1098000 912000, 760000 912000, 760000 1408000))',5070),'eb545b18-5498-43c8-8652-f73e16446cc0'),
	 ('c8bf6c6d-7f19-406a-a438-f2f876ce4815','souris-river','Souris River',ST_GeomFromText('POLYGON ((-708000 3100000, -178000 3100000, -178000 2736000, -708000 2736000, -708000 3100000))',5070),'33f03e9a-711b-41e7-9bdd-66152b69128d'),
	 ('ca7859d9-f58e-4c0e-a077-2440b33784eb','big-horn-river','Big Horn River',ST_GeomFromText('POLYGON ((-1132000 2634000, -850000 2634000, -850000 2226000, -1132000 2226000, -1132000 2634000))',5070),'1f579664-d1db-4ee9-897e-47c16dc55012'),
	 ('cb192e4d-38ed-4999-9fd8-7481a19ba475','white-river-1','White River',ST_GeomFromText('POLYGON ((154000 1648000, 524000 1648000, 524000 1352000, 154000 1352000, 154000 1648000))',5070),'60754640-fef3-429b-b2f4-efdcf3b61e55'),
	 ('cb5964ec-4bca-4600-9760-426f053940dd','salt-river-1','Salt River',ST_GeomFromText('POLYGON ((866000 1766000, 980000 1766000, 980000 1646000, 866000 1646000, 866000 1766000))',5070),'b952664c-4b11-4d85-89fa-a2cc405b1131'),
	 ('ced6ec9e-43b5-496e-a2b7-894af92c9b63','mississippi-river-navigation','Mississippi River Navigation',ST_GeomFromText('POLYGON ((48000 2646000, 564000 2646000, 564000 2204000, 48000 2204000, 48000 2646000))',5070),'33f03e9a-711b-41e7-9bdd-66152b69128d'),
	 ('cf193b4e-61c3-4e4d-9503-2935a82aed96','little-kanawha-river','Little Kanawha River',ST_GeomFromText('POLYGON ((1164000 1970000, 1354000 1970000, 1354000 1824000, 1164000 1824000, 1164000 1970000))',5070),'788cc853-235a-4e43-a136-b1f190a6a656'),
	 ('d0045c5f-823a-427e-834f-dc987bdf49f4','arkansas-river-2','Arkansas River',ST_GeomFromText('POLYGON ((-726000 1768000, 196000 1768000, 196000 1286000, -726000 1286000, -726000 1768000))',5070),'26e6c300-480b-4e22-afae-7cc27dd9b116'),
	 ('d212f4d6-8158-4020-89e7-54ccc1f8c4cb','rogue-river','Rogue River',ST_GeomFromText('POLYGON ((-2296000 2534000, -2088000 2534000, -2088000 2412000, -2296000 2412000, -2296000 2534000))',5070),'c18588b6-25ab-42c9-b31a-a33c585d0b49'),
	 ('d2c8b141-a26b-479e-acf2-fc51693d3887','obion-forked-deer-river','Obion-Forked Deer River',ST_GeomFromText('POLYGON ((558000 1580000, 692000 1580000, 692000 1378000, 558000 1378000, 558000 1580000))',5070),'8fc88b15-9cd4-4e86-8b8c-6d956926010b'),
	 ('d3b5a999-deb5-4c85-ad0b-838abeac9a70','malheur-river','Malheur River',ST_GeomFromText('POLYGON ((-1816000 2590000, -1656000 2590000, -1656000 2436000, -1816000 2436000, -1816000 2590000))',5070),'834ea54d-2454-425f-b443-50ba4ab46e28'),
	 ('d4c3c6ed-4745-4683-8287-563bba8f6ca4','apalachicola-chattahoochee-flint-rivers','Apalachicola Chattahoochee Flint Rivers',ST_GeomFromText('POLYGON ((970000 1386000, 1162000 1386000, 1162000 790000, 970000 790000, 970000 1386000))',5070),'eb545b18-5498-43c8-8652-f73e16446cc0'),
	 ('d67852f2-cbe8-4bf4-a43e-9244f12de45a','area-1','Area 1',ST_GeomFromText('POLYGON ((1548000 536000, 1584000 536000, 1584000 492000, 1548000 492000, 1548000 536000))',5070),'4142c26c-0407-41ad-b660-8657ddb2be69'),
	 ('d73f434f-1d7b-4f17-9079-f9af7a513d74','cuyama-river','Cuyama River',ST_GeomFromText('POLYGON ((-2190000 1644000, -2076000 1644000, -2076000 1536000, -2190000 1536000, -2190000 1644000))',5070),'89a1fe0c-03f3-47cf-8ee1-cd3de2e1ba7b'),
	 ('dc3fa4cd-2c8c-4149-9b26-d377d4f98f48','jacksonjames-river','JacksonJames River',ST_GeomFromText('POLYGON ((1346000 1848000, 1620000 1848000, 1620000 1688000, 1346000 1688000, 1346000 1848000))',5070),'7fd53614-f484-4dfd-8fc4-d11b11fb071c'),
	 ('dfe7c932-f41d-4b3a-aaf3-0e1a58103c78','black-warrior-and-tombigbee-river','Black Warrior and Tombigbee River',ST_GeomFromText('POLYGON ((626000 1332000, 906000 1332000, 906000 920000, 626000 920000, 626000 1332000))',5070),'eb545b18-5498-43c8-8652-f73e16446cc0'),
	 ('e04d4bbb-2141-4cbb-8171-7e4d3ba922db','deschutes','Deschutes',ST_GeomFromText('POLYGON ((-2082000 2768000, -1858000 2768000, -1858000 2514000, -2082000 2514000, -2082000 2768000))',5070),'cf0e2fde-9156-4a96-a8bc-32640cb0043d'),
	 ('e07bb447-d92d-4e3e-8696-5f4db7757414','columbia-river-2','Columbia River',ST_GeomFromText('POLYGON ((-2144000 2920000, -1694000 2920000, -1694000 2522000, -2144000 2522000, -2144000 2920000))',5070),'c18588b6-25ab-42c9-b31a-a33c585d0b49'),
	 ('e59276ff-1ed5-430b-a2ca-cb225f2d6596','colorado-river','Colorado River',ST_GeomFromText('POLYGON ((-734000 1228000, -38000 1228000, -38000 730000, -734000 730000, -734000 1228000))',5070),'a222e733-2fa7-4cd8-b3a6-065956e693f0'),
	 ('e157c054-8e51-4914-a250-63412c33f7f8','fort-peck','Fort Peck',ST_GeomFromText('POLYGON ((-1392000 2996000, -742000 2996000, -742000 2462000, -1392000 2462000, -1392000 2996000))',5070),'90173658-2de9-4329-926d-176c1b29089a'),
	 ('c8faba00-ad50-45e1-ad8d-658e445f350b','gavins-point-to-sioux-city','Gavins Point to Sioux City',ST_GeomFromText('POLYGON ((-316000 2770000, 38000 2770000, 38000 2136000, -316000 2136000, -316000 2770000))',5070),'90173658-2de9-4329-926d-176c1b29089a'),
	 ('e60a856e-a209-4950-b23f-ac227a719729','juniata-river','Juniata River',ST_GeomFromText('POLYGON ((1438000 2136000, 1592000 2136000, 1592000 2000000, 1438000 2000000, 1438000 2136000))',5070),'7d7e962d-e554-48f0-8f82-b762a31441a6'),
	 ('e627a104-4bba-45d1-a824-3b0bfdbe4bc4','tulare-lakebed','Tulare Lakebed',ST_GeomFromText('POLYGON ((-2180000 1822000, -1942000 1822000, -1942000 1546000, -2180000 1546000, -2180000 1822000))',5070),'df64a2de-91a2-4e6c-85c9-53d3d03f6794'),
	 ('e837f3e1-de8f-4ead-a38a-30d290972cea','sacramento-river','Sacramento River',ST_GeomFromText('POLYGON ((-2296000 2420000, -1962000 2420000, -1962000 1936000, -2296000 1936000, -2296000 2420000))',5070),'df64a2de-91a2-4e6c-85c9-53d3d03f6794'),
	 ('ef1ea885-60fe-4787-a25c-7a6a76889bcd','area-2','Area 2',ST_GeomFromText('POLYGON ((1544000 512000, 1582000 512000, 1582000 466000, 1544000 466000, 1544000 512000))',5070),'4142c26c-0407-41ad-b660-8657ddb2be69'),
	 ('f06761de-b4a5-400d-a37e-fdd6d25be33a','lower-colorado-river-1','Lower Colorado River',ST_GeomFromText('POLYGON ((-1778000 1774000, -1082000 1774000, -1082000 1214000, -1778000 1214000, -1778000 1774000))',5070),'89a1fe0c-03f3-47cf-8ee1-cd3de2e1ba7b'),
	 ('f2e9371c-83f7-4045-8d30-6ffbec61e29e','lower-columbia','Lower Columbia',ST_GeomFromText('POLYGON ((-2140000 2916000, -1920000 2916000, -1920000 2734000, -2140000 2734000, -2140000 2916000))',5070),'cf0e2fde-9156-4a96-a8bc-32640cb0043d'),
	 ('f3b03058-11e6-4fd2-9cb6-7cb53c9ab051','cache-river','Cache River',ST_GeomFromText('POLYGON ((574000 1630000, 626000 1630000, 626000 1576000, 574000 1576000, 574000 1630000))',5070),'0088df5f-ec58-4654-9b71-3590266b475c'),
	 ('f4219691-e498-46a3-ab0f-f2957bd09a10','minnesota-river','Minnesota River',ST_GeomFromText('POLYGON ((-112000 2602000, 234000 2602000, 234000 2244000, -112000 2244000, -112000 2602000))',5070),'33f03e9a-711b-41e7-9bdd-66152b69128d'),
	 ('f4f91608-c412-4187-b6bc-940ade81b9f2','lackawaxen-river','Lackawaxen River',ST_GeomFromText('POLYGON ((1676000 2278000, 1724000 2278000, 1724000 2204000, 1676000 2204000, 1676000 2278000))',5070),'6e3c2e48-a15a-4892-ba91-caab86499abc'),
	 ('f62ea39e-28e0-4db7-aace-fc804f003f02','little-river-1','Little River',ST_GeomFromText('POLYGON ((50000 1298000, 170000 1298000, 170000 1192000, 50000 1192000, 50000 1298000))',5070),'26e6c300-480b-4e22-afae-7cc27dd9b116'),
	 ('fa93c238-edf6-4288-bace-e49b43df76a9','upper-colorado-river','Upper Colorado River',ST_GeomFromText('POLYGON ((-1430000 2362000, -806000 2362000, -806000 1452000, -1430000 1452000, -1430000 2362000))',5070),'df64a2de-91a2-4e6c-85c9-53d3d03f6794'),
	 ('fbe7d5f1-9586-469b-a5aa-9eed8db438cd','big-muddy-river','Big Muddy River',ST_GeomFromText('POLYGON ((550000 1746000, 646000 1746000, 646000 1626000, 550000 1626000, 550000 1746000))',5070),'0088df5f-ec58-4654-9b71-3590266b475c'),
	 ('fc4f8be1-4584-4d64-9bb4-0754433a5c36','willow-creek-1','Willow Creek',ST_GeomFromText('POLYGON ((-1840000 2732000, -1800000 2732000, -1800000 2682000, -1840000 2682000, -1840000 2732000))',5070),'c18588b6-25ab-42c9-b31a-a33c585d0b49'),
	 ('fcbfbe4e-6a93-4659-b7e3-395adaf7f383','st-lucie-river','St Lucie River',ST_GeomFromText('POLYGON ((1544000 596000, 1578000 596000, 1578000 560000, 1544000 560000, 1544000 596000))',5070),'4142c26c-0407-41ad-b660-8657ddb2be69'),
	 ('fcd83908-3ac5-4c64-9792-3f3989e6f780','powder-river','Powder River',ST_GeomFromText('POLYGON ((-1750000 2670000, -1642000 2670000, -1642000 2582000, -1750000 2582000, -1750000 2670000))',5070),'834ea54d-2454-425f-b443-50ba4ab46e28'),
	 ('fecc8e15-b5e9-4a76-a69d-cba6194e8ca0','lacda-river','LACDA River',ST_GeomFromText('POLYGON ((-2130000 1566000, -1954000 1566000, -1954000 1410000, -2130000 1410000, -2130000 1566000))',5070),'89a1fe0c-03f3-47cf-8ee1-cd3de2e1ba7b'),
	 ('6f735edf-d2a0-4835-af39-18236c70be94','north-platte-river','North Platte River',ST_GeomFromText('POLYGON ((-1080000 2298000, -384000 2298000, -384000 1964000, -1080000 1964000, -1080000 2298000))',5070),'90173658-2de9-4329-926d-176c1b29089a'),
	 ('fdb77f5c-48c8-4d1a-ab35-f628ad36434b','south-platte-river','South Platte River',ST_GeomFromText('POLYGON ((-878000 2086000, -384000 2086000, -384000 1784000, -878000 1784000, -878000 2086000))',5070),'90173658-2de9-4329-926d-176c1b29089a'),
	 ('8babd199-c1f8-49b9-8e5a-d6b62ece3878','ia-mo-osage-river','IA MO Osage River',ST_GeomFromText('POLYGON ((-100000 2058000, 592000 2058000, 592000 1524000, -100000 1524000, -100000 2058000))',5070),'90173658-2de9-4329-926d-176c1b29089a'),
	 ('b31d4708-0f31-4799-9041-b60dba433b18','kansas-river','Kansas River',ST_GeomFromText('POLYGON ((-696000 2070000, 244000 2070000, 244000 1690000, -696000 1690000, -696000 2070000))',5070),'90173658-2de9-4329-926d-176c1b29089a'),
	 ('b4043cef-5cd1-4110-9a1c-2db333aae3f6','fpg_lwryel','FPG_LWRYEL',ST_GeomFromText('POLYGON ((-936000 2806000, -540000 2806000, -540000 2246000, -936000 2246000, -936000 2806000))',5070),'90173658-2de9-4329-926d-176c1b29089a'),
	 ('fef2cf95-2457-45a3-87d8-93f1eb7bc73b','fpg_milk_missouri','FPG_MILK_MISSOURI',ST_GeomFromText('POLYGON ((-1296000 3044000, -370000 3044000, -370000 2704000, -1296000 2704000, -1296000 3044000))',5070),'90173658-2de9-4329-926d-176c1b29089a'),
	 ('e97c5b9b-da0f-43ae-b7c4-d54bbdcc0e9f','fpg_upryell_bighorn','FPG_UPRYELL_BIGHORN',ST_GeomFromText('POLYGON ((-1188000 2678000, -852000 2678000, -852000 2226000, -1188000 2226000, -1188000 2678000))',5070),'90173658-2de9-4329-926d-176c1b29089a'),
	 ('f019ffec-e9d3-48e6-ab74-eaa8fd8065e0','garrison-to-oahe','GARRISON TO OAHE',ST_GeomFromText('POLYGON ((-842000 2814000, -194000 2814000, -194000 2210000, -842000 2210000, -842000 2814000))',5070),'90173658-2de9-4329-926d-176c1b29089a');