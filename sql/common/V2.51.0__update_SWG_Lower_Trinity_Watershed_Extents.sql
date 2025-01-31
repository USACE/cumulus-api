-- update SWG Lower Trinity Watershed Extents
-- xmin,ymax (top left), 
-- xmax ymax (top right), 
-- xmax ymin (bottom right), 
-- xmin ymin (bottom left), 
-- xmin ymax (top left again)
UPDATE watershed
	SET geometry = ST_GeomFromText(
        'POLYGON ((
    81520 859025, 
    131785 859025, 
    131785 731300, 
    81520 731300, 
    81520 859025))',5070)
WHERE id = '59e880ca-f242-4f9a-b1f8-06424f8bb23f';


