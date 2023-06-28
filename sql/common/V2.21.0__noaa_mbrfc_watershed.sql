-- extent to polygon reference order - simple 4 point extents
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
('a76386d1-aaa8-40e7-85ed-371b810715f2','mbrfc','Missouri Basin River Forecast Center (MBRFC)',ST_GeomFromText('POLYGON ((-1390000 3044000, 484000 3044000, 484000 1556000, -1390000 1556000, -1390000 3044000))', 5070),'4283e3a7-db01-4ddb-9592-e12a361c0b4c');