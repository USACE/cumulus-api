-- lower colorado watershed SPL district
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)
UPDATE watershed
	SET geometry = ST_GeomFromText('POLYGON((-1780654.3065809954 1211649.9311556690, -1780654.3065809954 1979314.8476487182, -1078683.3926492415 1979314.8476487182, -1078683.3926492415 1211649.9311556690, -1780654.3065809954 1211649.9311556690))',5070)
WHERE id = 'f06761de-b4a5-400d-a37e-fdd6d25be33a';