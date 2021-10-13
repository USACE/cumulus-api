-- area_group Nashville; Cumberland River and Tennesse River
INSERT INTO area_group (id, watershed_id, slug, name) VALUES
    ('e3fd63a1-f19f-4bf3-b436-1c7086b7afe7','c785f4de-ab17-444b-b6e6-6f1ad16676e8','subbasin','Subbasin'),
    ('6abacad1-8137-4cb1-adc2-c241b31f8761','c54eab5b-1020-476b-a5f8-56d77802d9bf','subbasin', 'Subbasin');

-- area_group_product_statistics_enabled
INSERT INTO area_group_product_statistics_enabled (area_group_id, product_id) VALUES
	('e3fd63a1-f19f-4bf3-b436-1c7086b7afe7', 'f1b6ac38-bbc9-48c6-bf78-207005ee74fa'),
    ('6abacad1-8137-4cb1-adc2-c241b31f8761', 'f1b6ac38-bbc9-48c6-bf78-207005ee74fa');
