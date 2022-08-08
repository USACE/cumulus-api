ALTER TABLE product ADD COLUMN acceptable_timedelta INTERVAL;

UPDATE cumulus.product SET acceptable_timedelta = '1 hour' where slug = 'ncep-rtma-ru-anl-airtemp';
UPDATE cumulus.product SET acceptable_timedelta = '2 hour' 
    where slug in ('ndgd-ltia98-airtemp', 'ndgd-leia98-precip', 'cbrfc-mpe', 'nbm-co-qpf', 'nbm-co-airtemp', 'hrrr-total-precip');
UPDATE cumulus.product SET acceptable_timedelta = '2 hour' WHERE slug LIKE '%01h%';
UPDATE cumulus.product SET acceptable_timedelta = '3 hour' WHERE slug LIKE '%03h%';
UPDATE cumulus.product SET acceptable_timedelta = '7 hour' WHERE slug LIKE '%06h%';
UPDATE cumulus.product SET acceptable_timedelta = '7 hour' WHERE slug IN ('wpc-qpf-2p5km');
UPDATE cumulus.product SET acceptable_timedelta = '50 hour' WHERE slug LIKE '%snodas%';
UPDATE cumulus.product SET acceptable_timedelta = '50 hour' WHERE slug LIKE 'prism-%-early';
UPDATE cumulus.product SET acceptable_timedelta = '6 months' WHERE slug LIKE 'prism-%-stable';
UPDATE cumulus.product SET acceptable_timedelta = NULL where slug = 'ncep-mrms-gaugecorr-qpe-01h';