-- slug = 'willow-creek-1'

-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)
UPDATE watershed
	SET geometry = ST_GeomFromText('POLYGON ((-1878600 2779900, -1795900 2779900, -1795900 2674000, -1878600 2674000, -1878600 2779900))',5070)
WHERE id = 'fc4f8be1-4584-4d64-9bb4-0754433a5c36';