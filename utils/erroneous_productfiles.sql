-- Find productfiles that are tagged as 'Forecast' but do not have a 
-- correct 'version' set.
select 
pf.id,
p.slug,
pf.datetime,
pf.file,
pf.version
from cumulus.product_tags pt
JOIN cumulus.product p on p.id = pt.product_id
JOIN cumulus.tag t on t.id = pt.tag_id
JOIN cumulus.productfile pf on pf.product_id = p.id
WHERE t.name = 'Forecast'
and pf.version < '1900-01-01'