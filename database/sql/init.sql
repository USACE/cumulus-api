\set ON_ERROR_STOP 1
begin;

\i '/sql/10-tables.sql'
\i '/sql/20-roles.sql'
\i '/sql/30-seed_data.sql'

commit;