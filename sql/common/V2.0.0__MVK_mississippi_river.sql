-- extent to polygon reference order - simple 4 point extents
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)

INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
('dc4134c8-4e85-4adc-a933-d42562edd6d3','mississippi-river-4','Mississippi River',ST_GeomFromText('POLYGON ((400000 1650000, 690000 1650000, 690000 870000, 400000 870000, 400000 1650000))',5070),'d02f876f-eb00-425b-aeca-09fa105d5bc2');