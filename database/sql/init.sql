\set ON_ERROR_STOP 1
begin;

\i '/sql/10-tables.sql'
\i '/sql/10a-views.sql'
\i '/sql/20-roles.sql'
\i '/sql/30-seed_data.sql'
\i '/sql/30a-seed_watershed.sql'
\i '/sql/31-seed_prodfiles.sql'
\i '/sql/32-seed_area_group_lrn.sql'
\i '/sql/33-seed_area_lrn.sql'
\i '/sql/34-seed_area_group_columbiariver.sql'
\i '/sql/35-seed_area_columbiariver.sql'

commit;