-- Cumulus Database Init
\set ON_ERROR_STOP 1
begin;

\i '/sql/01-domains.sql'
\i '/sql/02-profiles.sql'
\i '/sql/03-watersheds.sql'
\i '/sql/04-products.sql'
\i '/sql/05-downloads.sql'
\i '/sql/06-statistics.sql'
\i '/sql/12-functions-triggers.sql'
\i '/sql/20-roles.sql'
\i '/sql/31-seed_prodfiles.sql'
\i '/sql/32-seed_area_group_lrn.sql'
\i '/sql/33-seed_area_lrn.sql'
\i '/sql/34-seed_area_group_columbiariver.sql'
\i '/sql/35-seed_area_columbiariver.sql'
-- \i '/sql/36-seed_data_testuser.sql'

commit;