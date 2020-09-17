-- Users and Roles for HHD Instrumentation Webapp

-- User cumulus_user
-- Note: Substitute real password for 'password'
CREATE USER cumulus_user WITH ENCRYPTED PASSWORD 'password';

-- Role cumulus_reader
-- Tables specific to cumulus app
CREATE ROLE cumulus_reader;
GRANT SELECT ON
    office,
    parameter,
    basin,
    unit,
    product,
    productfile,
    acquirable,
    acquisition,
    acquirable_acquisition,
    key,
    v_download
TO cumulus_reader;

-- Role cumulus_writer
-- Tables specific to instrumentation app
CREATE ROLE cumulus_writer;
GRANT INSERT,UPDATE,DELETE ON 
    office,
    parameter,
    basin,
    unit,
    product,
    productfile,
    acquirable,
    acquisition,
    acquirable_acquisition,
    key
TO cumulus_writer;

-- Role postgis_reader
CREATE ROLE postgis_reader;
GRANT SELECT ON geometry_columns TO postgis_reader;
GRANT SELECT ON geography_columns TO postgis_reader;
GRANT SELECT ON spatial_ref_sys TO postgis_reader;

-- Grant Permissions to instrument_user
GRANT postgis_reader TO cumulus_user;
GRANT cumulus_reader TO cumulus_user;
GRANT cumulus_writer TO cumulus_user;
