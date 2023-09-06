-- CREATE OR REPLACE VIEW directives are throwing errors related to
-- https://github.com/USACE/cumulus-api/pull/426/commits/7749dc220a56b3f4f5c5492619aca1db6b76dbea
-- Explicitly calling DROP VIEW here, then counting on R__04_views_products.sql to recreate them immediately afterward.
DROP VIEW IF EXISTS v_productfile;
DROP VIEW IF EXISTS v_product;