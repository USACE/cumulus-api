
-- note: NWDP office already in database

-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    ('8f150e1a-676b-4c63-b337-ec3e2c98cce3','nwdp-columbia','Columbia River',ST_GeomFromText('POLYGON ((-2292000 3506000, -1100000 3506000, -1100000 2188000, -2292000 2188000, -2292000 3506000))', 5070),'85ba21d8-ba4b-4060-a519-a3e69c1e29ed');