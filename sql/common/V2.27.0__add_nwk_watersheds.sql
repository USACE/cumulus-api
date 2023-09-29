
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)

-- Chariton
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    ('d4019fd0-fdd2-452b-89ca-4b1937cb31ec','chariton','Chariton',ST_GeomFromText('POLYGON ((167000 2020000, 307000 2020000, 307000 1800000, 167000 1800000, 167000 2020000))', 5070),'07c1c91e-2e42-4fbc-a550-f775a27eb419');

-- Little Platte
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    ('9e2140d5-03e9-4f63-9cdf-e95008c92d8d','little-platte','Little Platte',ST_GeomFromText('POLYGON ((69000 1957000, 161000 1957000, 161000 1785000, 69000 1785000, 69000 1957000))', 5070),'07c1c91e-2e42-4fbc-a550-f775a27eb419');

-- Lower Kansas
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    ('ecce9393-c774-4413-ac45-3d1d99804e4c','lower-kansas','Lower Kansas',ST_GeomFromText('POLYGON ((-682000 2050000, 235000 2050000, 235000 1689000, -682000 1689000, -682000 2050000))', 5070),'07c1c91e-2e42-4fbc-a550-f775a27eb419');

-- Osage
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    ('b7de6454-9803-4792-93c5-34931506f5f8','osage','Osage',ST_GeomFromText('POLYGON ((-36700 1839000, 412000 1839000, 412000 1538000, -36700 1538000, -36700 1839000))', 5070),'07c1c91e-2e42-4fbc-a550-f775a27eb419');

 -- Upper Kansas
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    ('6b41b757-82d6-46b6-b729-c268ca662831','upper-kansas','Upper Kansas',ST_GeomFromText('POLYGON ((-682000 2038000, -47200 2038000, -47200 1689000, -682000 1689000, -682000 2038000))', 5070),'07c1c91e-2e42-4fbc-a550-f775a27eb419');   
    