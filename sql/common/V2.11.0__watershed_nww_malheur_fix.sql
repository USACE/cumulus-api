-- extent to polygon reference order - simple 4 point extents
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)
UPDATE watershed 
SET geometry = ST_GeomFromText('POLYGON ((-1860000 2630000, -1600000 2630000, -1600000 2380000, -1860000 2380000, -1860000 2630000))',5070)
WHERE id = 'd3b5a999-deb5-4c85-ad0b-838abeac9a70';