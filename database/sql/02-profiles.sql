-- extensions
CREATE extension IF NOT EXISTS "uuid-ossp";


-- drop tables if they already exist
drop table if exists
    public.profile,
    public.profile_token
    CASCADE;

-- profile
CREATE TABLE IF NOT EXISTS public.profile (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    edipi BIGINT UNIQUE NOT NULL,
    username VARCHAR(240) UNIQUE NOT NULL,
    email VARCHAR(240) UNIQUE NOT NULL,
    is_admin boolean NOT NULL DEFAULT false
);

-- Profile (Faked with: https://homepage.net/name_generator/)
-- NOTE: EDIPI 1 should not be used; test user with EDIPI = 1 created by integration tests
INSERT INTO profile (id, edipi, is_admin, username, email) VALUES
    ('57329df6-9f7a-4dad-9383-4633b452efab',2,true,'AnthonyLambert','anthony.lambert@fake.usace.army.mil'),
    ('f320df83-e2ea-4fe9-969a-4e0239b8da51',3,false,'MollyRutherford','molly.rutherford@fake.usace.army.mil'),
    ('89aa1e13-041a-4d15-9e45-f76eba3b0551',4,false,'DominicGlover','dominic.glover@fake.usace.army.mil'),
    ('405ab7e1-20fc-4d26-a074-eccad88bf0a9',5,false,'JoeQuinn','joe.quinn@fake.usace.army.mil'),
    ('81c77210-6244-46fe-bdf6-35da4f00934b',6,false,'TrevorDavidson','trevor.davidson@fake.usace.army.mil'),
    ('f056201a-ffec-4f5b-aec5-14b34bb5e3d8',7,false,'ClaireButler','claire.butler@fake.usace.army.mil'),
    ('9effda27-49f7-4745-8e55-fa819f550b09',8,false,'SophieBower','sophie.bower@fake.usace.army.mil'),
    ('37407aba-904a-42fa-af73-6ab748ee1f98',9,false,'NeilMcLean','neil.mclean@fake.usace.army.mil'),
    ('c0fd72ae-cccc-45c9-ba1d-4353170c352d',10,false,'JakeBurgess','jake.burgess@fake.usace.army.mil'),
    ('be549c16-3f65-4af4-afb6-e18c814c44dc',11,false,'DanQuinn','dan.quinn@fake.usace.army.mil'),
    ('8dde311e-1761-4d3f-ac13-a458d17fe432',29, true, 'Cumulus Automation','cumulus@usace.army.mil');


-- profile_token
CREATE TABLE IF NOT EXISTS public.profile_token (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    token_id VARCHAR NOT NULL,
    profile_id UUID NOT NULL REFERENCES profile(id),
    issued TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    hash VARCHAR(240) NOT NULL
);
