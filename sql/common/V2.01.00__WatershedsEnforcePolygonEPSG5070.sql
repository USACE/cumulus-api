DROP VIEW IF EXISTS v_watershed;

ALTER TABLE watershed
    ALTER COLUMN geometry
        TYPE geometry(Geometry, 5070);

-- The view should get replaced in R__03_views_watersheds.sql
