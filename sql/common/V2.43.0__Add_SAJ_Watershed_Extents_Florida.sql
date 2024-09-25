--(xmin ymax, xmax ymax, xmax ymin, xmin ymin, xmin ymax)

-- notes

--Buffered extends from qgis

--xmin = 989539.3071116814
--xmax = 1671778.6007457851
--ymax = 978696.9156769654
--ymin = 385612.5100058009

--After rounding by hand

--xmin = 989500
--xmax = 1671800
--ymax = 978700
--ymin = 340000
-- 4142c26c-0407-41ad-b660-8657ddb2be69 - SAJ ID
-- providede by Adam bfbd5b34-ff07-41d4-87cf-d67c80f98be1

-- add new watershed
INSERT INTO watershed (id, slug, "name", geometry, office_id, output_srid) VALUES
	 ('bfbd5b34-ff07-41d4-87cf-d67c80f98be1','florida','Florida',ST_GeomFromText('POLYGON ((989500 978700, 1671800 978700, 1671800 340000, 989500 340000, 989500 978700))',5070),'4142c26c-0407-41ad-b660-8657ddb2be69', 5070);