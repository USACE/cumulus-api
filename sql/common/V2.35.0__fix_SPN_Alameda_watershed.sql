-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)
UPDATE watershed
	SET geometry = ST_GeomFromText('POLYGON ((-2267700 1961500, -2192100 1961500, -2192100 1869000, -2267700 1869000, -2267700 1961500))',5070)
WHERE id = '965e523a-08b4-4567-8b9f-4ac8882fb0e1';