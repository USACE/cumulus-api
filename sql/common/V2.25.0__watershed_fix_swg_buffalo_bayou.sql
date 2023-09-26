-- extent to polygon reference order - simple 4 point extents
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)
UPDATE watershed 
    SET geometry = ST_GeomFromText('POLYGON ((-2300 786000, 96000 786000, 96000 718000, -2300 718000, -2300 786000))',5070)
WHERE id = 'c3082967-c74e-4931-9da6-118d761b43b5';