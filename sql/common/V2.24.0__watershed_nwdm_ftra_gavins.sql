-- extent to polygon reference order - simple 4 point extents
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
     ('d41831ea-74ae-4cf9-b1ed-9e173b875ffd','ftra-to-gavins', 'FTRA to Gavins', ST_GeomFromText('POLYGON ((-710000 2302000, -112400 2302000, -112400 2114000, -710000 2114000 , -710000 2302000))',5070), '90173658-2de9-4329-926d-176c1b29089a');