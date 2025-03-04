-- remove fields from product table that have been migrated to product_series

ALTER TABLE product
DROP COLUMN label,
DROP COLUMN dss_fpart,
DROP COLUMN parameter_id,
DROP COLUMN description,
DROP COLUMN unit_id,
DROP COLUMN suite_id,
DROP COLUMN dss_datatype_id;