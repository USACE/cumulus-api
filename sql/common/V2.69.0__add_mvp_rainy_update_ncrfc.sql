-- add new watershed MVP Rain Lake Basin
INSERT INTO watershed (id, 
                        slug, 
                        "name", 
                        geometry, 
                        office_id, 
                        output_srid) 
VALUES
	 ('827b58f7-7755-4e77-a9ce-69137936a3fe',
     'rainy-lake-basin',
     'Rainy Lake Basin',
ST_GeomFromText('Polygon ((
                        18017 3006247,
                        476118 3006247,
                        476118 2705665,
                        18017 2705665,
                        18017 3006247))',
                                5070),
    '33f03e9a-711b-41e7-9bdd-66152b69128d', 
    5070);



-- update ncrfc watershed extents
UPDATE watershed
	SET geometry = ST_GeomFromText('Polygon ((
                        -844108 3158884,
                        1256918 3158884,
                        1256918 1584817,
                        -844108 1584817,
                        -844108 3158884))',
                                5070)
WHERE id = '03784645-2ccb-4e77-b391-1ee7e613c3c4';

