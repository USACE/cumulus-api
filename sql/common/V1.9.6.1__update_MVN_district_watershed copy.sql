-- extent to polygon reference order - simple 4 point extents
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)

UPDATE watershed 
SET geometry =  ST_GeomFromText('POLYGON ((180000 1082000, 800000 1082000, 800000 572000, 180000 572000, 180000 1082000))',5070)
WHERE id = '6a7a6848-1cd3-4be5-ab0f-ea0296c951d0';
