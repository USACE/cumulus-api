-- BasinComps Configuration and Rolling Totals Enhancement

-- Basin configuration: maps each basin to its product list
CREATE TABLE IF NOT EXISTS basincomps_basin_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    basin_id VARCHAR(100) NOT NULL,
    basin_name VARCHAR(255),
    product_ids UUID[] NOT NULL,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(basin_id)
);

CREATE INDEX IF NOT EXISTS idx_basincomps_basin_config_basin ON basincomps_basin_config(basin_id);
CREATE INDEX IF NOT EXISTS idx_basincomps_basin_config_enabled ON basincomps_basin_config(enabled);

-- View to show basin config with product names
CREATE OR REPLACE VIEW v_basincomps_basin_config AS
SELECT
    bc.id,
    bc.basin_id,
    bc.basin_name,
    bc.product_ids,
    (SELECT array_agg(p.label ORDER BY p.label)
     FROM product p
     WHERE p.id = ANY(bc.product_ids)) AS product_names,
    (SELECT array_agg(p.slug ORDER BY p.slug)
     FROM product p
     WHERE p.id = ANY(bc.product_ids)) AS product_slugs,
    bc.enabled,
    bc.created_at,
    bc.updated_at
FROM basincomps_basin_config bc;

-- Rolling totals table: stores aggregated precipitation totals
CREATE TABLE IF NOT EXISTS basincomps_rolling_total (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_date TIMESTAMPTZ NOT NULL,
    data_date DATE NOT NULL,              -- The end date of the rolling period
    basin_id VARCHAR(100) NOT NULL,
    basin_name VARCHAR(255),
    product_id UUID REFERENCES product(id),
    product_slug VARCHAR(100),
    days INTEGER NOT NULL,                -- Number of days (1, 2, 3, 4, 5, 6, 7)
    total_value DOUBLE PRECISION,         -- Total precipitation over the period
    units VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(basin_id, product_id, data_date, days)
);

CREATE INDEX IF NOT EXISTS idx_basincomps_rolling_run_date ON basincomps_rolling_total(run_date DESC);
CREATE INDEX IF NOT EXISTS idx_basincomps_rolling_data_date ON basincomps_rolling_total(data_date DESC);
CREATE INDEX IF NOT EXISTS idx_basincomps_rolling_basin ON basincomps_rolling_total(basin_id, data_date);
CREATE INDEX IF NOT EXISTS idx_basincomps_rolling_product ON basincomps_rolling_total(product_id, data_date);
CREATE INDEX IF NOT EXISTS idx_basincomps_rolling_days ON basincomps_rolling_total(days);

-- Note: Views are created in R__11_views_basincomps.sql (repeatable migration)
-- This allows them to reference v_product which is created in R__04_views_products.sql

COMMENT ON TABLE basincomps_basin_config IS 'Configuration mapping each basin to its list of products for analysis';
COMMENT ON TABLE basincomps_rolling_total IS 'Rolling precipitation totals (1-7 days) per basin and product';
COMMENT ON COLUMN basincomps_rolling_total.days IS 'Number of days in rolling total (1, 2, 3, 4, 5, 6, 7)';
COMMENT ON COLUMN basincomps_rolling_total.data_date IS 'End date of the rolling period';
