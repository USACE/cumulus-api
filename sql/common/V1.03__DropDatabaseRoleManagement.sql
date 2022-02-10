DROP VIEW IF EXISTS v_profile;
DROP VIEW IF EXISTS v_watershed_roles; 
DROP TABLE profile_token CASCADE;
DROP TABLE watershed_roles CASCADE;
DROP TABLE role CASCADE;
DROP TABLE my_watersheds CASCADE;
DROP TABLE download CASCADE;
DROP TABLE profile CASCADE;

-- my_watersheds
CREATE TABLE IF NOT EXISTS my_watersheds (
	sub UUID NOT NULL,
    watershed_id UUID NOT NULL REFERENCES watershed(id) ON DELETE CASCADE,
    CONSTRAINT sub_unique_watershed UNIQUE(sub, watershed_id)
);

-- download
CREATE TABLE IF NOT EXISTS download (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
	sub UUID NOT NULL,
    datetime_start TIMESTAMPTZ NOT NULL,
    datetime_end TIMESTAMPTZ NOT NULL,
    progress INTEGER NOT NULL DEFAULT 0,
    status_id UUID REFERENCES download_status(id),
    watershed_id UUID REFERENCES watershed(id),
    file VARCHAR(240),
    processing_start TIMESTAMPTZ NOT NULL DEFAULT now(),
    processing_end TIMESTAMPTZ
);
