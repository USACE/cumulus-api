--------
-- ROLES
--------
-- For a production-ready deployment scenario, the role 'cumulus_user' with a complicated selected password
-- should already exist, having been created when the database was stood-up.
-- The statement below is used to create database user for developing locally with Docker Compose with a
-- simple password ('cumulus_pass'). https://stackoverflow.com/questions/8092086/create-postgresql-role-user-if-it-doesnt-exist
DO $$
BEGIN
  CREATE USER cumulus_user WITH ENCRYPTED PASSWORD 'cumulus_pass';
  EXCEPTION WHEN DUPLICATE_OBJECT THEN
  RAISE NOTICE 'not creating role cumulus_user -- it already exists';
END
$$;

-- Role cumulus_reader;
DO $$
BEGIN
  CREATE ROLE cumulus_reader;
  EXCEPTION WHEN DUPLICATE_OBJECT THEN
  RAISE NOTICE 'not creating role cumulus_reader -- it already exists';
END
$$;

-- Role cumulus_writer
DO $$
BEGIN
  CREATE ROLE cumulus_writer;
  EXCEPTION WHEN DUPLICATE_OBJECT THEN
  RAISE NOTICE 'not creating role cumulus_writer -- it already exists';
END
$$;

-- Role postgis_reader
DO $$
BEGIN
  CREATE ROLE postgis_reader;
  EXCEPTION WHEN DUPLICATE_OBJECT THEN
  RAISE NOTICE 'not creating role postgis_reader -- it already exists';
END
$$;

-- Role postgis_reader
GRANT SELECT ON geometry_columns TO postgis_reader;
GRANT SELECT ON geography_columns TO postgis_reader;
GRANT SELECT ON spatial_ref_sys TO postgis_reader;

-- Grant Permissions to cumulus_user
GRANT postgis_reader TO cumulus_user;
GRANT cumulus_reader TO cumulus_user;
GRANT cumulus_writer TO cumulus_user;

-- Set Search Path
ALTER ROLE cumulus_user SET search_path TO cumulus,topology,public;

-- Grant Schema Usage to cumulus_user
GRANT USAGE ON SCHEMA cumulus TO cumulus_user;

-- Role cumulus_reader
GRANT SELECT ON
    area,
    area_group,
    area_group_product_statistics_enabled,
    config,
    profile,
    profile_token,
    office,
    parameter,
    role,
    unit,
    product,
    productfile,
    product_tags,
    suite,
    tag,
    acquirable,
    acquirablefile,
    download_status,
    download,
    download_product,
    watershed,
    my_watersheds,
    watershed_roles
TO cumulus_reader;

-- Role cumulus_writer
GRANT INSERT,UPDATE,DELETE ON
    area,
    area_group,
    area_group_product_statistics_enabled,
    config,
    profile,
    profile_token,
    office,
    parameter,
    role,
    unit,
    product,
    productfile,
    suite,
    tag,
    product_tags,
    acquirable,
    acquirablefile,
    download_status,
    download,
    download_product,
    watershed,
    watershed_roles,
    my_watersheds
TO cumulus_writer;
