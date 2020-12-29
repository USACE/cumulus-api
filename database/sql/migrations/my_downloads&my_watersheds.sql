-- 28-Dec-2020
-- Adds objects for my_downloads & my_watersheds

-- Add profile_id to DOWNLOAD table
ALTER TABLE public.download ADD COLUMN profile_id UUID REFERENCES profile(id);

-- Add new PROFILE_WATERSHEDS table
CREATE TABLE IF NOT EXISTS public.profile_watersheds (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    watershed_id UUID NOT NULL REFERENCES watershed(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES profile(id) ON DELETE CASCADE,
    CONSTRAINT profile_unique_watershed UNIQUE(watershed_id, profile_id)

);

-- Replace v_download
CREATE OR REPLACE VIEW v_download AS (
        SELECT d.id AS id,
            d.datetime_start AS datetime_start,
            d.datetime_end AS datetime_end,
            d.progress AS progress,
            d.file AS file,
            d.processing_start AS processing_start,
            d.processing_end AS processing_end,
            d.status_id AS status_id,
            d.watershed_id AS watershed_id,
            d.profile_id AS profile_id,
            w.slug         AS watershed_slug,
            w.name         AS watershed_name,
            s.name AS status,
            dp.product_id AS product_id
        FROM download d
            INNER JOIN download_status s ON d.status_id = s.id
            INNER JOIN watershed w on w.id = d.watershed_id
            INNER JOIN (
                SELECT array_agg(id) as product_id,
                    download_id
                FROM download_product
                GROUP BY download_id
            ) dp ON d.id = dp.download_id
            ORDER BY d.processing_start DESC
    );

-- Role cumulus_reader
GRANT SELECT ON profile_watersheds,v_download TO cumulus_reader;
-- Role cumulus_writer
GRANT SELECT ON profile_watersheds TO cumulus_writer;