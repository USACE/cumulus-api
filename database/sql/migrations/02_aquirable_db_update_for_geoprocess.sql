-- ####################
-- Acquirable Table
-- ####################

-- Remove schedule column
alter table acquirable drop column schedule;

-- Add 'slug' column
alter table acquirable add column slug varchar(120) not null default '';
update acquirable set slug = replace(lower(name), '_', '-');
alter table acquirable add unique (slug);

-- ####################
-- AcquirableFile Table
-- ####################

CREATE TABLE IF NOT EXISTS public.acquirablefile (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    datetime TIMESTAMPTZ NOT NULL,
    file VARCHAR(1200) NOT NULL,
    create_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    process_date TIMESTAMPTZ,
    acquirable_id UUID not null REFERENCES acquirable (id)
);

-- ####################
-- ProductFile Table
-- ####################

-- Add acquirablefile_id FK
-- this should be NOT NULL after all existing ProductFile records have a UUID for acquirablefile_id
alter table productfile add column acquirablefile_id UUID REFERENCES acquirablefile (id);