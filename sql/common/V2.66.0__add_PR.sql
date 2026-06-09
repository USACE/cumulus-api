-- add saa district
INSERT INTO office (id, symbol, name) VALUES
    ('cae8e3a6-37a1-4fbc-856b-acb68dbf666c','SAA','Caribbean District');

-- add new watershed SAA Puerto Rico
INSERT INTO watershed (id, 
                        slug, 
                        "name", 
                        geometry, 
                        office_id, 
                        output_srid) 
VALUES
	 ('26d1728f-3ce1-4a84-b0e6-bbdc7ead1f83',
     'puerto-rico',
     'Puerto Rico and US Virgin Islands',
        ST_GeomFromText('Polygon ((
                        2637127 588520,
                        3880772 588520,
                        3880772 -604377,
                        2637127 -604377,
                        2637127 588520))',
                                5070),
    'cae8e3a6-37a1-4fbc-856b-acb68dbf666c', 
    5070);


-- update Great Lakes watershed name
UPDATE watershed SET name = 'Great Lakes Basin' WHERE slug = 'great-lakes';

                 