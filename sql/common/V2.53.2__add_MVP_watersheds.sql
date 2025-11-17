--(xmin ymax, xmax ymax, xmax ymin, xmin ymin, xmin ymax)

-- add new watershed MVP Bois de Sioux River
INSERT INTO watershed (id, 
                        slug, 
                        "name", 
                        geometry, 
                        office_id, 
                        output_srid) 
VALUES
	 ('374cf5e0-c935-40c6-8b96-c33a1c8e579f',
     'bois-de-sioux',
     'Bois de Sioux River',
    ST_GeomFromText('Polygon ((
                            -88720 2698951,
                            55404 2698951,
                            55404 2494540,
                            -88720 2494540,
                            -88720 2698951))',
                                    5070),
    '33f03e9a-711b-41e7-9bdd-66152b69128d', 
    5070);


-- add new watershed MVP Park River
INSERT INTO watershed (id, 
                        slug, 
                        "name", 
                        geometry, 
                        office_id, 
                        output_srid) 
VALUES
	 ('4bff8a03-93d2-4579-aa0c-a65afc2066b6',
     'park-mvp',
     'Park River',
        ST_GeomFromText('Polygon ((
                                -176350 2863898,
                                -83643 2863898,
                                -83643 2815127,
                                -176350 2815127,
                                -176350 2863898))',
                                        5070),
    '33f03e9a-711b-41e7-9bdd-66152b69128d', 
    5070);


-- add new watershed MVP Red Lake River
INSERT INTO watershed (id, 
                        slug, 
                        "name", 
                        geometry, 
                        office_id, 
                        output_srid) 
VALUES
	 ('157a95a9-665f-46d6-b0eb-cc3497da141f',
     'red-lake',
     'Red lake River',
    ST_GeomFromText('Polygon ((
                            -77926 2841800,
                            146064 2841800,
                            146064 2714875,
                            -77926 2714875,
                            -77926 2841800))',
                                    5070),
    '33f03e9a-711b-41e7-9bdd-66152b69128d', 
    5070);


-- add new watershed MVP Sheyenne River
INSERT INTO watershed (id, 
                        slug, 
                        "name", 
                        geometry, 
                        office_id, 
                        output_srid) 
VALUES
	 ('b9feb168-a692-4c04-8a36-5e9cd5868e7a',
     'sheyenne-river',
     'Sheyenne River',
    ST_GeomFromText('Polygon ((
                            -352090 2815523,
                            -77217 2815523,
                            -77217 2583070,
                            -352090 2583070,
                            -352090 2815523))',
                                    5070),
    '33f03e9a-711b-41e7-9bdd-66152b69128d', 
    5070);