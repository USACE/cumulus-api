-- CREATE OR REPLACE VIEW directives are throwing errors related to
-- https://github.com/USACE/cumulus-api/commit/91981b57236a832b388fa897417e4205f09c3c92#diff-2bd0a1d914ab4d5a618b1a4ffff044715d557ccad8ab529d9c01f5c9f58d8a01
-- Explicitly calling DROP VIEW here, then counting on R__04_views_products.sql and R__05_views_downloads.sql to recreate them immediately afterward.
DROP VIEW IF EXISTS v_productfile;
DROP VIEW IF EXISTS v_product;
DROP VIEW IF EXISTS v_download_request;
