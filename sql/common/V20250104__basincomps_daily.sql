-- BasinComps Daily Results Schema
-- Stores basin average precipitation computed daily by HEC-MetVue BasinComps

-- Daily basin averages computed by BasinComps
CREATE TABLE IF NOT EXISTS basincomps_daily_result (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_date TIMESTAMPTZ NOT NULL,       -- Timestamp of batch run with timezone (for timezone-aware date filtering)
    data_date DATE NOT NULL,             -- Date of the precipitation data
    data_datetime TIMESTAMPTZ NOT NULL,  -- Full timestamp of the data with timezone
    basin_id VARCHAR(100) NOT NULL,      -- Basin identifier from shapefile
    basin_name VARCHAR(255),             -- Basin name from shapefile
    product_id UUID REFERENCES product(id),
    product_slug VARCHAR(100),
    interval_hours INTEGER,              -- Time interval (e.g., 1 hour)
    value DOUBLE PRECISION,              -- Average precipitation value
    units VARCHAR(20),                   -- Units (mm, in, etc)
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_basincomps_daily_run_date ON basincomps_daily_result(run_date DESC);
CREATE INDEX IF NOT EXISTS idx_basincomps_daily_data_date ON basincomps_daily_result(data_date DESC);
CREATE INDEX IF NOT EXISTS idx_basincomps_daily_basin ON basincomps_daily_result(basin_id, data_date);
CREATE INDEX IF NOT EXISTS idx_basincomps_daily_product ON basincomps_daily_result(product_id, data_date);

-- Batch run log
CREATE TABLE IF NOT EXISTS basincomps_batch_run (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_date TIMESTAMPTZ NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    status VARCHAR(20),                  -- SUCCESS, FAILED, RUNNING
    product_ids UUID[],                  -- Products processed
    file_count INTEGER,                  -- Number of files processed
    result_count INTEGER,                -- Number of results inserted
    csv_file_key TEXT,                   -- S3 key for CSV output
    dss_file_key TEXT,                   -- S3 key for DSS output
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_basincomps_batch_run_date ON basincomps_batch_run(run_date DESC);

-- Note: Views are created in R__11_views_basincomps.sql (repeatable migration)
-- This allows them to reference v_product which is created in R__04_views_products.sql
