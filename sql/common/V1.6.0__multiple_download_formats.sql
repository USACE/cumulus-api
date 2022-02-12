-- download_format
CREATE TABLE IF NOT EXISTS download_format (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    abbreviation VARCHAR(120) UNIQUE NOT NULL,
    name VARCHAR(120) NOT NULL,
    extension VARCHAR(120) NOT NULL
);

INSERT INTO download_format (id, abbreviation, name, extension) VALUES
    ('215b13c1-f710-4688-a8ac-5a9e7d991bb0','tgz-cog','Gzip Compressed Tape Archive (tar)','tar.gz'),
    ('358d3ee2-dfdc-47ae-a104-b98613e6578b','dss7','HEC-DSS Version 7', 'dss');

-- https://stackoverflow.com/questions/512451/how-can-i-add-a-column-that-doesnt-allow-nulls-in-a-postgresql-database
-- Set download_format_id corresponding to 'dss7' for all existing downloads in the database
ALTER TABLE download ADD COLUMN download_format_id UUID NOT NULL DEFAULT '358d3ee2-dfdc-47ae-a104-b98613e6578b' REFERENCES download_format(id);
-- Drop Default
ALTER TABLE download ALTER COLUMN download_format_id DROP DEFAULT;
