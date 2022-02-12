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

ALTER TABLE download ADD COLUMN download_format_id UUID NOT NULL REFERENCES download_format(id);
