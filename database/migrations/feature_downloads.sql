drop table if exists 
    public.download_status,
    public.download,
    public.download_product
    CASCADE;

-- download_status_id
CREATE TABLE IF NOT EXISTS public.download_status (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(120) NOT NULL
);

INSERT INTO download_status(id, name) VALUES 
('a553101e-8c51-4ddd-ac2e-b011ed54389b', 'FAILED'),
('94727878-7a50-41f8-99eb-a80eb82f737a', 'INITIATED'),
('3914f0bd-2290-42b1-bc24-41479b3a846f', 'SUCCESS');



-- download
CREATE TABLE IF NOT EXISTS public.download (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    datetime_start TIMESTAMPTZ NOT NULL,
    datetime_end TIMESTAMPTZ NOT NULL,
    progress INTEGER NOT NULL DEFAULT 0,
    status_id UUID REFERENCES download_status(id),
    basin_id UUID REFERENCES basin(id),
    file VARCHAR(240),
    processing_start TIMESTAMPTZ NOT NULL DEFAULT now(),
    processing_end TIMESTAMPTZ
);

-- download_product
CREATE TABLE IF NOT EXISTS public.download_product (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES product(id),
    download_id UUID REFERENCES download(id)
);

GRANT SELECT ON
    download_status,
    download,
    download_product
TO cumulus_reader;

-- Role cumulus_writer
-- Tables specific to instrumentation app
GRANT INSERT,UPDATE,DELETE ON
    download_status,
    download,
    download_product
TO cumulus_writer;
