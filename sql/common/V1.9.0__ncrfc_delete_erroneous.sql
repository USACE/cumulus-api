-- ncrfc surface airtemp forecast removed to correct product as realtime
-- child tables have ON DELETE CASCADE linked to product table

-- NCRFC, Airtemp 1hr
-- ncrfc-fmat-01h
DELETE from productfile
where product_id = '71644147-5910-4e65-9195-43c37fc6ddc6'

DELETE FROM product
WHERE id = '71644147-5910-4e65-9195-43c37fc6ddc6';

DELETE FROM acquirablefile
WHERE acquirable_id = '28d16afe-2834-4d2c-9df2-fdf2c40e510f';

DELETE FROM acquirable
WHERE id = '28d16afe-2834-4d2c-9df2-fdf2c40e510f';



-- -- MARFC, NBM Airtemp 3hr
-- -- marfc-nbmt-03h
DELETE from productfile
where product_id = '4b556067-9610-42fc-a71d-0fa0fcbd8ea1'

DELETE FROM product
WHERE id = '4b556067-9610-42fc-a71d-0fa0fcbd8ea1';

DELETE FROM acquirablefile
WHERE acquirable_id = 'e2228d8c-204a-4c7e-849b-a9a7e5c13eca';

DELETE FROM acquirable
WHERE id = 'e2228d8c-204a-4c7e-849b-a9a7e5c13eca';