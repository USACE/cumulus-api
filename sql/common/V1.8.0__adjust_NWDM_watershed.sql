-- extent to polygon reference order - simple 4 point extents
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)

-- sioux-city-to-rulo
-- 4a952583-09cd-4f1a-8887-87b32f19932c
UPDATE watershed set geometry = ST_GeomFromText('POLYGON ((-568000 2320000, 180000 2320000, 180000 1823000, -568000 1823000, -568000 2320000))',5070) WHERE id = '4a952583-09cd-4f1a-8887-87b32f19932c';