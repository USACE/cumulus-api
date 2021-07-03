-- Users and Roles for HHD Instrumentation Webapp

-- User cumulus_user
-- Note: Substitute real password for 'password'
CREATE USER cumulus_user WITH ENCRYPTED PASSWORD 'password';
CREATE ROLE cumulus_reader;
CREATE ROLE cumulus_writer;
CREATE ROLE postgis_reader;

-- Set Search Path
ALTER ROLE cumulus_user SET search_path TO cumulus,topology,public;

-- Grant Schema Usage to cumulus_user
GRANT USAGE ON SCHEMA cumulus TO cumulus_user;

--------------------------------------------------------------------------
-- NOTE: IF USERS ALREADY EXIST ON DATABASE, JUST RUN FROM THIS POINT DOWN
--------------------------------------------------------------------------

-- Role cumulus_reader
-- Tables specific to cumulus app
GRANT SELECT ON
    area,
    area_group,
    area_group_product_statistics_enabled,
    config,
    profile,
    profile_token,
    office,
    parameter,
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
    watershed_roles,
    v_acquirablefile,
    v_download,
    v_download_request,
    v_area_5070,
    v_product,
    v_productfile,
    v_watershed,
    v_watershed_roles,
    v_profile
TO cumulus_reader;

-- Role cumulus_writer
-- Tables specific to instrumentation app
GRANT INSERT,UPDATE,DELETE ON
    area,
    area_group,
    area_group_product_statistics_enabled,
    config,
    profile,
    profile_token,
    office,
    parameter,
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

-- Role postgis_reader
GRANT SELECT ON geometry_columns TO postgis_reader;
GRANT SELECT ON geography_columns TO postgis_reader;
GRANT SELECT ON spatial_ref_sys TO postgis_reader;

-- Grant Permissions to instrument_user
GRANT postgis_reader TO cumulus_user;
GRANT cumulus_reader TO cumulus_user;
GRANT cumulus_writer TO cumulus_user;