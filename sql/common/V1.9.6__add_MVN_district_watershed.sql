-- extent to polygon reference order - simple 4 point extents
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)

INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
('6a7a6848-1cd3-4be5-ab0f-ea0296c951d0','new-orleans-district','New Orleans District',ST_GeomFromText('POLYGON ((190000 1050000, 760000 1050000, 760000 600000, 190000 600000, 190000 1050000))',5070),'26dab361-76a0-4cb2-b5a5-01667ab7f7da');

