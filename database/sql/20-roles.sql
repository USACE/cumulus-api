-- Users and Roles for HHD Instrumentation Webapp

-- User cumulus_user
-- Note: Substitute real password for 'password'
CREATE USER cumulus_user WITH ENCRYPTED PASSWORD 'password';
CREATE ROLE cumulus_reader;
CREATE ROLE cumulus_writer;
CREATE ROLE postgis_reader;

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
    product_group,
    acquirable,
    acquisition,
    acquirable_acquisition,
    acquirablefile,
    download_status,
    download,
    download_product,
    watershed,
    profile_watersheds,
    v_acquirablefile,
    v_download,
    v_area_5070,
    v_watershed
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
    product_group,
    acquirable,
    acquisition,
    acquirable_acquisition,
    acquirablefile,
    download_status,
    download,
    download_product,
    watershed,
    profile_watersheds
TO cumulus_writer;

-- Role postgis_reader
GRANT SELECT ON geometry_columns TO postgis_reader;
GRANT SELECT ON geography_columns TO postgis_reader;
GRANT SELECT ON spatial_ref_sys TO postgis_reader;

-- Grant Permissions to instrument_user
GRANT postgis_reader TO cumulus_user;
GRANT cumulus_reader TO cumulus_user;
GRANT cumulus_writer TO cumulus_user;
