-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)
UPDATE watershed 
	SET geometry = ST_GeomFromText('POLYGON ((-2180000 3517000, -1090000 3517000, -1090000 2178000, -2180000 2178000, -2180000 3517000))', 5070)
WHERE id = '8f150e1a-676b-4c63-b337-ec3e2c98cce3';