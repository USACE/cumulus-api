--(xmin ymax, xmax ymax, xmax ymin, xmin ymin, xmin ymax)

-- add new watershed LRE Great Lakes Watershed
INSERT INTO watershed (id, 
                        slug, 
                        "name", 
                        geometry, 
                        office_id, 
                        output_srid) 
VALUES
	 ('09c53d56-a2b7-4c62-a180-2b78b6834a63',
     'great-lakes',
     'Great Lakes',
        ST_GeomFromText('Polygon ((
                        147342 3257822,
                        1833194 3257822,
                        1833194 1890482,
                        147342 1890482,
                        147342 3257822))',
                                5070),
    '586ac79a-083e-4c8c-8438-9585a88a4b3d', 
    5070);

