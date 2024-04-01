--(xmin ymax, xmax ymax, xmax ymin, xmin ymin, xmin ymax)
-- upper columbia
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('2c9f5b9e-3711-44ca-9281-2568d46d154b','upper-columbia-nwdp','Upper Columbia',ST_GeomFromText('POLYGON ((-5400000 11530000, -4650000 11530000, -4650000 10100000, -4650000 10100000, -5400000 11530000))',5070),'85ba21d8-ba4b-4060-a519-a3e69c1e29ed');

--Spokane
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('0bdb19bb-4c9f-46ae-9a4d-58c0ee76176e','spokane-nwdp','Spokane',ST_GeomFromText('POLYGON ((-5480000 9800000, -4730000 9800000, -4730000 9210000, -4730000 9210000, -5480000 9800000))',5070),'85ba21d8-ba4b-4060-a519-a3e69c1e29ed');

--Middle Columbia
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('f0079104-1e6d-4d02-bebd-1bfb7b39443d','middle-columbia-nwdp','Middle Columbia',ST_GeomFromText('POLYGON ((-6180000 10750000, -5120000 10750000, -5120000 9230000, -5120000 9230000, -6180000 10750000))',5070),'85ba21d8-ba4b-4060-a519-a3e69c1e29ed');

--Yakima
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('39965245-a319-4bf5-9bee-3a8a066ef15f','yakima-nwdp','Yakima',ST_GeomFromText('POLYGON ((-6360000 9800000, -5820000 9800000, -5820000 9130000, -5820000 9130000, -6360000 9800000))',5070),'85ba21d8-ba4b-4060-a519-a3e69c1e29ed');

--Mainstem Columbia
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('95c2e769-142f-43c9-8b03-673b552f2dbd','mainstem-columbia-nwdp','Mainstem Columbia',ST_GeomFromText('POLYGON ((-6590000 9430000, -5560000 9430000, -5560000 8350000, -5560000 8350000, -6590000 9430000))',5070),'85ba21d8-ba4b-4060-a519-a3e69c1e29ed');

--Deschutes
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('3e55dd02-377a-4b4c-af3e-5b31c5db2b05','deschutes-nwdp','Deschutes',ST_GeomFromText('POLYGON ((-6830000 9090000, -6090000 9090000, -6090000 8250000, -6090000 8250000, -6830000 9090000))',5070),'85ba21d8-ba4b-4060-a519-a3e69c1e29ed');

--Lower Colubia
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    	 ('bf2f6e42-04f8-432c-b369-c960c1f0d564','lower-columbia-nwdp','Lower Columbia',ST_GeomFromText('POLYGON ((-7030000 9580000, -6300000 9580000, -6300000 8970000, -6300000 8970000, -7030000 9580000))',5070),'85ba21d8-ba4b-4060-a519-a3e69c1e29ed');