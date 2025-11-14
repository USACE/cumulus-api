-- Always re-apply when running migrations: ${flyway:timestamp}
-- BasinComps Views
-- These views reference v_product, which is created in R__04_views_products.sql
-- By putting views in a repeatable migration, they run after versioned migrations

-- v_basincomps_daily_result
-- View for easy querying of daily basin average results with product names
CREATE OR REPLACE VIEW v_basincomps_daily_result AS
SELECT
    r.id,
    r.run_date,
    r.data_date,
    r.data_datetime,
    r.basin_id,
    r.basin_name,
    r.product_id,
    vp.name AS product_name,
    r.product_slug,
    r.interval_hours,
    r.value,
    r.units,
    r.created_at
FROM basincomps_daily_result r
LEFT JOIN v_product vp ON vp.id = r.product_id;

-- v_basincomps_rolling_total
-- View for easy querying of rolling precipitation totals with product names
CREATE OR REPLACE VIEW v_basincomps_rolling_total AS
SELECT
    rt.id,
    rt.run_date,
    rt.data_date,
    rt.basin_id,
    rt.basin_name,
    rt.product_id,
    vp.name AS product_name,
    rt.product_slug,
    rt.days,
    rt.total_value,
    rt.units,
    rt.created_at
FROM basincomps_rolling_total rt
LEFT JOIN v_product vp ON vp.id = rt.product_id;

-- v_basincomps_shapefile_config
-- View to show shapefile config with product names and slugs
CREATE OR REPLACE VIEW v_basincomps_shapefile_config AS
SELECT
    sc.id,
    sc.config_name,
    sc.description,
    sc.shapefile_path,
    sc.product_ids,
    (SELECT array_agg(vp.name ORDER BY vp.name)
     FROM v_product vp
     WHERE vp.id = ANY(sc.product_ids)) AS product_names,
    (SELECT array_agg(vp.slug ORDER BY vp.slug)
     FROM v_product vp
     WHERE vp.id = ANY(sc.product_ids)) AS product_slugs,
    sc.enabled,
    sc.created_at,
    sc.updated_at
FROM basincomps_shapefile_config sc;

-- Grant SELECT permissions to cumulus_reader
GRANT SELECT ON
    v_basincomps_daily_result,
    v_basincomps_rolling_total,
    v_basincomps_shapefile_config
TO cumulus_reader;
