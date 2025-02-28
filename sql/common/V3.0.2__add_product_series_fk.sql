-- add the product_series_id foreign key to product table

ALTER TABLE product
ADD COLUMN product_series_id UUID REFERENCES product_series(id);


-- assign product_series_id to the corresponding products

UPDATE product p
SET product_series_id = ps.id
FROM product_series ps
WHERE p.slug = ps.slug;

UPDATE product p
SET product_series_id = (
    SELECT id 
    FROM product_series 
    WHERE slug = 'ndfd-conus-airtemp'
)
WHERE slug LIKE 'ndfd-conus-airtemp-%';