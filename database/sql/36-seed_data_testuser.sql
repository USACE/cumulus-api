-- Add test user
INSERT INTO public.profile (id, edipi, is_admin, username, email) VALUES 
    ('659f787d-f069-4049-ba94-5b6d2f2dbfeb', 0, false, 'test.user', 'test@usace.army.mil');

-- Add User's Watersheds
INSERT INTO public.my_watersheds (watershed_id, profile_id) VALUES 
    ('225faeef-4251-4e97-9901-2c3c480180d3', '659f787d-f069-4049-ba94-5b6d2f2dbfeb'),
    ('2778d7eb-5ef6-419a-823d-3cf5a1cdad0b', '659f787d-f069-4049-ba94-5b6d2f2dbfeb'),
    ('442e9ee0-d1d1-4f30-94b6-17d2bdcfe8f2', '659f787d-f069-4049-ba94-5b6d2f2dbfeb'),
    ('5580c215-3b32-414c-809c-e43277867729', '659f787d-f069-4049-ba94-5b6d2f2dbfeb');

-- Add User's Downloads
INSERT INTO public.download (id, datetime_start, datetime_end, progress, status_id, watershed_id, file, processing_start, processing_end, profile_id) VALUES
    ('084b7cbe-2db7-44e3-b0f2-f18b6577b557', '2020-11-30 19:00:00', '2020-12-03 19:00:00', 0, 'a553101e-8c51-4ddd-ac2e-b011ed54389b', 'c88676cc-b1c0-4d2c-9a88-ca86956f281b', null, '2020-12-28 20:21:24', null, '659f787d-f069-4049-ba94-5b6d2f2dbfeb'),
    ('6af712cb-f10c-40a5-8d58-494e5750c9ab', '2020-12-06 19:00:00', '2020-12-08 19:00:00', 100, '3914f0bd-2290-42b1-bc24-41479b3a846f', '048ce853-6642-4ac4-9fb2-81c01f67a85b', 'cumulus/download/dss/download_6af712cb-f10c-40a5-8d58-494e5750c9ab.dss', '2020-12-28 20:27:15', '2020-12-28 20:27:18', '659f787d-f069-4049-ba94-5b6d2f2dbfeb');

-- Add User's download_product
INSERT INTO public.download_product (id, product_id, download_id) VALUES
    ('64b7607e-25d1-4d4b-b0fc-bf5059fd082e', 'f1b6ac38-bbc9-48c6-bf78-207005ee74fa', '084b7cbe-2db7-44e3-b0f2-f18b6577b557'),
    ('7c759949-06b1-4b1d-801f-a2e35022acf8', '86526298-78fa-4307-9276-a7c0a0537d15', '6af712cb-f10c-40a5-8d58-494e5750c9ab');