-- extensions
CREATE extension IF NOT EXISTS "uuid-ossp";


-- drop tables if they already exist
drop table if exists
    public.download,
    public.download_product,
    public.download_status
	CASCADE;


-- download_status_id
CREATE TABLE IF NOT EXISTS public.download_status (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(120) NOT NULL
);

-- download
CREATE TABLE IF NOT EXISTS public.download (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    datetime_start TIMESTAMPTZ NOT NULL,
    datetime_end TIMESTAMPTZ NOT NULL,
    progress INTEGER NOT NULL DEFAULT 0,
    status_id UUID REFERENCES download_status(id),
    watershed_id UUID REFERENCES watershed(id),
    file VARCHAR(240),
    processing_start TIMESTAMPTZ NOT NULL DEFAULT now(),
    processing_end TIMESTAMPTZ,
    profile_id UUID REFERENCES profile(id)
);

-- download_product
CREATE TABLE IF NOT EXISTS public.download_product (
    download_id UUID REFERENCES download(id),
    product_id UUID REFERENCES product(id),
    PRIMARY KEY (download_id, product_id)
);


-- -----
-- VIEWS
-- -----

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
                SELECT array_agg(product_id) as product_id,
                       download_id
                FROM download_product
                GROUP BY download_id
            ) dp ON d.id = dp.download_id
            ORDER BY d.processing_start DESC
    );


-- ---------
-- SEED DATA
-- ---------

INSERT INTO download_status (id, name) VALUES
    ('94727878-7a50-41f8-99eb-a80eb82f737a', 'INITIATED'),
    ('3914f0bd-2290-42b1-bc24-41479b3a846f', 'SUCCESS'),
    ('a553101e-8c51-4ddd-ac2e-b011ed54389b', 'FAILED');