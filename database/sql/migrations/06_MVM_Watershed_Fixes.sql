-- Castor River and Headwaters
UPDATE cumulus.watershed 
set geometry=ST_GeomFromText('POLYGON ((482000 1654000, 580000 1654000, 580000 1570000, 482000 1570000, 482000 1654000))', 5070)  
where id ='5580c215-3b32-414c-809c-e43277867729';

-- St Johns Bayou
UPDATE cumulus.watershed 
set geometry=ST_GeomFromText('POLYGON ((556000 1596000, 616000 1596000, 616000 1514000, 556000 1514000, 556000 1596000))',5070)
where id ='13ee536a-b752-4730-aaca-068c0a2a37d3';

-- White River Basin
UPDATE cumulus.watershed 
set geometry=ST_GeomFromText('POLYGON ((334000 1526000, 520000 1526000, 520000 1224000, 334000 1224000, 334000 1526000))', 5070)
where id ='571ecb91-c212-4149-9198-1139c01a1cc4';