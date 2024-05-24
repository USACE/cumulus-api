-- eau galle watershed MVP district
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)
UPDATE watershed
	SET geometry = ST_GeomFromText('POLYGON ((286452 2457298, 332064 2457298, 332064 2384560, 286452 2384560, 286452 2457298))',5070)
WHERE id = '03206ff6-fe91-426c-a5e9-4c651b06f9c6';