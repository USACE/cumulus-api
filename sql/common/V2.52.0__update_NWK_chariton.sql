-- update NWK Chariton 
-- xmin,ymax (top left), 
-- xmax ymax (top right), 
-- xmax ymin (bottom right), 
-- xmin ymin (bottom left), 
-- xmin ymax (top left again)
UPDATE watershed
	SET geometry = ST_GeomFromText(
        'POLYGON ((
            175000 2020000, 
            309000 2020000, 
            309000 1790000, 
            175000 1790000, 
            175000 2020000))',
        5070)
WHERE id = 'd4019fd0-fdd2-452b-89ca-4b1937cb31ec';