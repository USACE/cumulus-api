-- extent to polygon reference order - simple 4 point extents
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)

-- mvk-red-river
UPDATE watershed 
SET geometry = ST_GeomFromText('POLYGON ((68000 1202000, 480000 1202000, 480000 888000, 68000 888000, 68000 1202000))',5070)
WHERE id = '8ea237ca-7705-409c-9ee8-c4d987072c85';

-- ouachita-black-river
UPDATE watershed
SET geometry = ST_GeomFromText('POLYGON ((146000 1322000, 480000 1322000, 480000 880000, 146000 880000, 146000 1322000))',5070)
WHERE id = '3bfc0f1a-49c9-4c27-a990-924d5255a926';