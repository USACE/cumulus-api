-- HRRR updated from per-cum to inst-val
UPDATE product
SET temporal_duration = 3600
WHERE id = '002125d6-2c90-4c24-9382-10a535d398bb';
