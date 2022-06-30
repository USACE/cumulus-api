--original
--1484000 1624000, 1664000 1624000, 1664000 1494000, 1484000 1494000, 1484000 1624000

--adjust xmax from 1664000 to 1720000 to cover right side of watershed

-- extent to polygon reference order - simple 4 point extents
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)
UPDATE watershed 
set geometry = ST_GeomFromText('POLYGON ((1484000 1624000, 1720000 1624000, 1720000 1494000, 1484000 1494000, 1484000 1624000))',5070)
WHERE id = '686026c0-bc68-45e8-95c6-1ccb0aec6682';