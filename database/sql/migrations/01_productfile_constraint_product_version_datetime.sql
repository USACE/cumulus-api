ALTER TABLE productfile ADD COLUMN version TIMESTAMPTZ;

ALTER TABLE productfile ADD CONSTRAINT unique_product_version_datetime UNIQUE(product_id, version, datetime);

ALTER TABLE productfile DROP CONSTRAINT product_unique_datetime;
