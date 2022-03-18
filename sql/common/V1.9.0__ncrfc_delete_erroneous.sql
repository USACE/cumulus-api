-- ncrfc surface airtemp forecast removed to correct product as realtime
-- child tables have ON DELETE CASCADE linked to product table
DELETE FROM product AS p WHERE p.id = '71644147-5910-4e65-9195-43c37fc6ddc6'