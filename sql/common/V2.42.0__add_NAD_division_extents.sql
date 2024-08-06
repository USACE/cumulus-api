--(xmin ymax, xmax ymax, xmax ymin, xmin ymin, xmin ymax)

-- notes
/**********************
Buffered extends from qgis

xmin = 1340639.4172334445
xmax = 2273786.7519109705
ymax = 3022943.4285793114
ymin = 1621502.6879133785

After rounding by hand

xmin = 1340000
xmax = 2274000
ymax = 3024000
ymin = 1620000

*********************/

-- add new watershed
INSERT INTO watershed (id, slug, "name", geometry, office_id, output_srid) VALUES
	 ('55b3c581-3b61-431c-91a6-580273713bf5','north-atlantic-division','North Atlantic Division',ST_GeomFromText('POLYGON ((1340000 3024000, 2274000 3024000, 2274000 1620000, 1340000 1620000, 1340000 3024000))',5070),'0cac2b45-a5df-49b3-9176-7d5145681958', 5070);