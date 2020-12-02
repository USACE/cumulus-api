\set ON_ERROR_STOP 1
begin;

\i '/docker-entrypoint-initdb.d/sql/10-tables.sql'
\i '/docker-entrypoint-initdb.d/sql/20-roles.sql'
\i '/docker-entrypoint-initdb.d/sql/30-seed_data.sql'

commit;