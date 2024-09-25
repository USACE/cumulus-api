--(xmin ymax, xmax ymax, xmax ymin, xmin ymin, xmin ymax)

/****************

xmin = -1019200
xmax = -553629
ymax = 2814812
ymin = 2237778

****************/

INSERT INTO watershed (id, slug, "name", geometry, office_id, output_srid) VALUES
('7794bf19-3969-4ec5-b801-47a7ad828523','lower-yellowstone','Lower Yellowstone',ST_GeomFromText('POLYGON ((-1019200 2814812, -553629 2814812, -553629 2237778, -1019200 2237778, -1019200 2814812))',5070),'1f579664-d1db-4ee9-897e-47c16dc55012', 5070);