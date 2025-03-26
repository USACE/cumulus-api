--(xmin ymax, xmax ymax, xmax ymin, xmin ymin, xmin ymax)

-- add new watershed LRD 
INSERT INTO watershed (id, 
                        slug, 
                        "name", 
                        geometry, 
                        office_id, 
                        output_srid) 
VALUES
	 ('81bcd301-9f10-4a11-b427-236bf9600333',
     'great-lakes-and-ohio-river-division',
     'Great Lakes and Ohio River Division',
     ST_GeomFromText('Polygon ((
                        194739 2853233, 
                        1765284 2853233, 
                        1765284 1253782, 
                        194739 1253782, 
                        194739 2853233))',
                                5070),
    'd0b7ddca-a321-44bd-bf2c-059c9c8cbe23', 
    5070);



    -- add new watershed MVD 
INSERT INTO watershed (id, 
                        slug, 
                        "name", 
                        geometry, 
                        office_id, 
                        output_srid) 
VALUES
	 ('f105db9f-33e7-4111-a187-0063881fbd00',
     'mississippi-valley-division',
     'Mississippi Valley Division',
     ST_GeomFromText('Polygon ((
                                -594586 2949315, 
                                716709 2949315, 
                                716709 645956, 
                                -594586 645956, 
                                -594586 2949315))',
                                5070),
    'dd580032-c210-4f98-8ab7-bda92ff2fe5e', 
    5070);


    -- add new watershed SWD 
INSERT INTO watershed (id, 
                        slug, 
                        "name", 
                        geometry, 
                        office_id, 
                        output_srid) 
VALUES
	 ('b183c5a4-fd84-4e68-abe9-ff8f80d1cd0f',
     'southwestern-division',
     'Soutwestern Division',
     ST_GeomFromText('Polygon ((
                            -659885 1760540, 
                            518375 1760540, 
                            518375 310915, 
                            -659885 310915, 
                            -659885 1760540))',
                                5070),
    'fe551ee7-3b04-440c-89a4-162dffd99ed2', 
    5070);


    -- add new watershed NWD 
INSERT INTO watershed (id, 
                        slug, 
                        "name", 
                        geometry, 
                        office_id, 
                        output_srid) 
VALUES
	 ('1ab99505-5573-490b-8989-a65f5bf11a2a',
     'northwestern-division',
     'Northwestern Division',
     ST_GeomFromText('Polygon ((
                            -2300802 3177668, 
                            505509 3177668, 
                            505509 1556205, 
                            -2300802 1556205, 
                            -2300802 3177668))',
                                5070),
    'd3da00c9-f839-4add-90a9-73053292d196', 
    5070);    


        -- add new watershed SPD 
INSERT INTO watershed (id, 
                        slug, 
                        "name", 
                        geometry, 
                        office_id, 
                        output_srid) 
VALUES
	 ('8c8a182e-bfba-4393-afad-80ed448df683',
     'south-pacific-division',
     'South Pacific Division',
     ST_GeomFromText('Polygon ((
                        -2361594 2538339, 
                        -490291 2538339, 
                        -490291 681639, 
                        -2361594 681639, 
                        -2361594 2538339))',
                                5070),
    '2222f2f5-d512-41ee-83d7-3a6cfcbf5bfb', 
    5070);    