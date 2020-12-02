drop table if exists 
	public.profile_token,
	public.profile,
    public.key
    CASCADE;

-- profile
CREATE TABLE IF NOT EXISTS public.profile (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    edipi BIGINT UNIQUE NOT NULL,
    email VARCHAR(240) UNIQUE NOT NULL
);

-- profile_token
CREATE TABLE IF NOT EXISTS public.profile_token (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    token_id VARCHAR NOT NULL,
    profile_id UUID NOT NULL REFERENCES profile(id),
    issued TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    hash VARCHAR(240) NOT NULL
);

GRANT SELECT ON
    profile,
    profile_token
TO cumulus_reader;

-- Role cumulus_writer
-- Tables specific to instrumentation app
GRANT INSERT,UPDATE,DELETE ON
    profile,
    profile_token
TO cumulus_writer;
