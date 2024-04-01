--(xmin ymax, xmax ymax, xmax ymin, xmin ymin, xmin ymax)
-- upper columbia
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('2c9f5b9e-3711-44ca-9281-2568d46d154b','upper-columbia-nwdp','Upper Columbia',ST_GeomFromText('POLYGON ((-1645920 3514344, -1417320 3514344, -1417320 3078480, -1645920 3078480, -1645920 3514344))',5070),'85ba21d8-ba4b-4060-a519-a3e69c1e29ed');

--Spokane
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('0bdb19bb-4c9f-46ae-9a4d-58c0ee76176e','spokane-nwdp','Spokane',ST_GeomFromText('POLYGON ((-1670304 2987040, -1441704 2987040, -1441704 2807208, -1670304 2807208, -1670304 2987040))',5070),'85ba21d8-ba4b-4060-a519-a3e69c1e29ed');

--Middle Columbia
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('f0079104-1e6d-4d02-bebd-1bfb7b39443d','middle-columbia-nwdp','Middle Columbia',ST_GeomFromText('POLYGON ((-1883664 3276600, -1560576 3276600, -1560576 2813304, -1883664 2813304, -1883664 3276600))',5070),'85ba21d8-ba4b-4060-a519-a3e69c1e29ed');

--Yakima
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('39965245-a319-4bf5-9bee-3a8a066ef15f','yakima-nwdp','Yakima',ST_GeomFromText('POLYGON ((-1938528 2987040, -1773936 2987040, -1773936 2782824, -1938528 2782824, -1938528 2987040))',5070),'85ba21d8-ba4b-4060-a519-a3e69c1e29ed');

--Mainstem Columbia
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('95c2e769-142f-43c9-8b03-673b552f2dbd','mainstem-columbia-nwdp','Mainstem Columbia',ST_GeomFromText('POLYGON ((-2008632 2874264, -1694688 2874264, -1694688 2545080, -2008632 2545080, -2008632 2874264))',5070),'85ba21d8-ba4b-4060-a519-a3e69c1e29ed');

--Deschutes
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('3e55dd02-377a-4b4c-af3e-5b31c5db2b05','deschutes-nwdp','Deschutes',ST_GeomFromText('POLYGON ((-2081784 2770632, -1856232 2770632, -1856232 2514600, -2081784 2514600, -2081784 2770632))',5070),'85ba21d8-ba4b-4060-a519-a3e69c1e29ed');

--Lower Colubia
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('bf2f6e42-04f8-432c-b369-c960c1f0d564','lower-columbia-nwdp','Lower Columbia',ST_GeomFromText('POLYGON ((-2142744 2919984, -1920240 2919984, -1920240 2734056, -2142744 2734056, -2142744 2919984))',5070),'85ba21d8-ba4b-4060-a519-a3e69c1e29ed');