--(xmin ymax, xmax ymax, xmax ymin, xmin ymin, xmin ymax)

-- notes
/**********************
Buffered extends from qgis

xmin = 568874.1243952705
xmax = 1849182.0687952701
ymax = 1744158.1616769086
ymin = 260833.8135769093

After rounding by hand

xmin = 568000
xmax = 1849200
ymax = 1760000
ymin = 260800

*********************/

-- add new watershed
INSERT INTO watershed (id, slug, "name", geometry, office_id, output_srid) VALUES
	 ('d05afc00-cecb-4987-8c58-8b1647ce00a7','south-atlantic-division','South Atlantic Division',ST_GeomFromText('POLYGON ((568000 1760000, 1849200 1760000, 1849200 260800, 568000 260800, 568000 1760000))',5070),'790ec8cf-8dad-48c9-bea9-9b8c26d29471', 5070);