-- update tables that link products to other components to use the
-- product_series FK rather than the product FK where appropriate

-- Temporarily drop views to avoid conflicts

DROP VIEW IF EXISTS v_download_request;
DROP VIEW IF EXISTS v_download;
DROP VIEW IF EXISTS v_productfile;
DROP VIEW IF EXISTS v_product;


-- product_tags

ALTER TABLE product_tags ADD COLUMN product_series_id UUID;

UPDATE product_tags pt
SET product_series_id = p.product_series_id
FROM product p
WHERE pt.product_id = p.id;

ALTER TABLE product_tags DROP CONSTRAINT product_tags_product_id_fkey;

ALTER TABLE product_tags DROP COLUMN product_id;

ALTER TABLE product_tags
ADD CONSTRAINT unique_tag_product_series UNIQUE(tag_id,product_series_id);

ALTER TABLE product_tags 
ADD CONSTRAINT product_tags_product_series_id_fkey
FOREIGN KEY (product_series_id) REFERENCES product_series(id) ON DELETE CASCADE;


-- download_product

ALTER TABLE download_product ADD COLUMN product_series_id UUID;

UPDATE download_product dp
SET product_series_id = p.product_series_id
FROM product p
WHERE dp.product_id = p.id;

ALTER TABLE download_product DROP CONSTRAINT download_product_product_id_fkey;

ALTER TABLE download_product DROP COLUMN product_id;

ALTER TABLE download_product 
ADD CONSTRAINT download_product_product_series_id_fkey
FOREIGN KEY (product_series_id) REFERENCES product_series(id) ON DELETE CASCADE;


-- area_group_product_statistics_enabled

ALTER TABLE area_group_product_statistics_enabled ADD COLUMN product_series_id UUID;

UPDATE area_group_product_statistics_enabled ag
SET product_series_id = p.product_series_id
FROM product p
WHERE ag.product_id = p.id;

ALTER TABLE area_group_product_statistics_enabled DROP CONSTRAINT area_group_product_statistics_enabled_product_id_fkey;

ALTER TABLE area_group_product_statistics_enabled DROP COLUMN product_id;

ALTER TABLE area_group_product_statistics_enabled 
ADD CONSTRAINT area_group_product_statistics_enabled_product_series_id_fkey
FOREIGN KEY (product_series_id) REFERENCES product_series(id) ON DELETE CASCADE;