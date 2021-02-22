ALTER TABLE productfile ADD CONSTRAINT product_unique_datetime UNIQUE(product_id, datetime);
