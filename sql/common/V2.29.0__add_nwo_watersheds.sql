
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)

-- Belle Fourche River
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('269fc819-3b87-4e92-adf3-dd435b232f6d','belle-fourche-river','Belle Fourche River',ST_GeomFromText('POLYGON ((-810000 2493000, -588000 2493000, -588000 2313000, -810000 2313000, -810000 2493000))',5070),'1f579664-d1db-4ee9-897e-47c16dc55012');

-- Bighorn
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('52cf2580-0baf-44f6-adc0-7f752f022121','bighorn','Bighorn',ST_GeomFromText('POLYGON ((-1145000 2644500, -851000 2644500, -851000 2212000, -1145000 2212000, -1145000 2644500))',5070),'1f579664-d1db-4ee9-897e-47c16dc55012');

-- Canyon Ferry
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('c9b088a4-c7ef-4b10-a847-f164166768e3','canyon-ferry','Canyon Ferry',ST_GeomFromText('POLYGON ((-1407700 2905000, -1079000 2905000, -1079000 2446000, -1407700 2446000, -1407700 2905000))',5070),'1f579664-d1db-4ee9-897e-47c16dc55012');

-- Fall River
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('8341ffc9-cd1b-45f8-9c95-27611368daae','fall-river','Fall River',ST_GeomFromText('POLYGON ((-637000 2341000, -576000 2341000, -576000 2270000, -637000 2270000, -637000 2341000))',5070),'1f579664-d1db-4ee9-897e-47c16dc55012');

-- Grand River
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('896ea8c2-718b-4ac0-a20d-8f10a4aa3faf','grand-river','Grand River',ST_GeomFromText('POLYGON ((-630500 2626500, -332000 2626500, -332000 2482600, -630500 2482600, -630500 2626500))',5070),'1f579664-d1db-4ee9-897e-47c16dc55012');

-- Heart River
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('0d516456-8430-4e7d-87c4-e99805fee4e8','heart-river','Heart River',ST_GeomFromText('POLYGON ((-580200 2727200, -351500 2727200, -351500 2588500, -580200 2588500, -580200 2727200))',5070),'1f579664-d1db-4ee9-897e-47c16dc55012');

-- James River
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('9fff6392-4212-4e83-a2c6-ec163fa67961','james-river','James River',ST_GeomFromText('POLYGON ((-329000 2781400, -132000 2781400, -132000 2533500, -329000 2533500, -329000 2781400))',5070),'1f579664-d1db-4ee9-897e-47c16dc55012');

-- Lower South Platte
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('1ab00492-dcdf-4ca3-bb1b-4e17c7319911','lower-south-platte','Lower South Platte',ST_GeomFromText('POLYGON ((-849700 2100000, -371500 2100000, -371500 1793600, -849700 1793600, -849700 2100000))',5070),'1f579664-d1db-4ee9-897e-47c16dc55012');

-- Marias
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('e43ea55d-867a-4cdb-a300-0ab7b23d7ddd','marias','Marias',ST_GeomFromText('POLYGON ((-1317100 3010400, -1047100 3010400, -1047100 2786700, -1317100 2786700, -1317100 3010400))',5070),'1f579664-d1db-4ee9-897e-47c16dc55012');

-- North Platte
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('53a7eab0-498f-4bb2-b9fa-3511a45e32e4','north-platte','North Platte',ST_GeomFromText('POLYGON ((-1092900 2310300, -371500 2310300, -371500 1951400, -1092900 1951400, -1092900 2310300))',5070),'1f579664-d1db-4ee9-897e-47c16dc55012');

-- Papio Creek
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('8cecebaa-b01d-4e78-8464-c1c5019a2bc1','papio-creek','Papio Creek',ST_GeomFromText('POLYGON ((-44000 2084900, 29000 2084900, 29000 1989600, -44000 1989600, -44000 2084900))',5070),'1f579664-d1db-4ee9-897e-47c16dc55012');

-- Rapid Creek
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('3366cde1-2200-40e3-bacf-fcd3c3f07ddb','rapid-creek','Rapid Creek',ST_GeomFromText('POLYGON ((-655200 2405800, -529700 2405800, -529700 2324100, -655200 2324100, -655200 2405800))',5070),'1f579664-d1db-4ee9-897e-47c16dc55012');

-- Salt Creek
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('1fad0b69-b357-4e7f-b094-38433ae1e693','salt-creek','Salt Creek',ST_GeomFromText('POLYGON ((-105000 2065600, -5800 2065600, -5800 1927900, -105000 1927900, -105000 2065600))',5070),'1f579664-d1db-4ee9-897e-47c16dc55012');

-- Upper South Platte
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('64060d1d-107b-424b-8705-7d5f49f4eb23','upper-south-platte','Upper South Platte',ST_GeomFromText('POLYGON ((-891100 1935100, -710000 1935100, -710000 1771700, -891100 1771700, -891100 1935100))',5070),'1f579664-d1db-4ee9-897e-47c16dc55012');
