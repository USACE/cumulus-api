INSERT INTO office (id, symbol, name) VALUES
('4283e3a7-db01-4ddb-9592-e12a361c0b4c', 'NOAA-NWS', 'National Weather Service');


-- extent to polygon reference order - simple 4 point extents
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
('17cb1eb9-7573-4010-bf3e-3692215be13a','abrfc','Arkansas-Red Basin River Forecast Center (ABRFC)',ST_GeomFromText('POLYGON ((-908000 1868000, 368000 1868000, 368000 1146000, -908000 1146000, -908000 1868000))', 5070),'4283e3a7-db01-4ddb-9592-e12a361c0b4c'),
('9b3d5d1d-ff7e-474b-a4b9-7963af99376a','cbrfc','Colorado Basin River Forecast Center (CBRFC)',ST_GeomFromText('POLYGON ((-1776000 2358000, -810000 2358000, -810000 998000, -1776000 998000, -1776000 2358000))', 5070),'4283e3a7-db01-4ddb-9592-e12a361c0b4c'),
('bd8d5663-50b1-4284-b2e2-f9e42eefcb53','cnrfc','California Nevada River Forecast Center (CNRFC)',ST_GeomFromText('POLYGON ((-2358000 2542000, -1518000 2542000, -1518000 1242000, -2358000 1242000, -2358000 2542000))', 5070),'4283e3a7-db01-4ddb-9592-e12a361c0b4c'),
('9d114f73-6c7a-49fa-9540-dd91be4baf27','lmrfc','Lower Mississippi River Forecast Center (LMRFC)',ST_GeomFromText('POLYGON ((-24000 1704000, 1294000 1704000, 1294000 672000, -24000 672000, -24000 1704000))', 5070),'4283e3a7-db01-4ddb-9592-e12a361c0b4c'),
('59d04e09-0c04-41fc-a39f-a64c104f66eb','marfc','Middle Atlantic River Forecast Center (MARFC)',ST_GeomFromText('POLYGON ((1350000 2406000, 1844000 2406000, 1844000 1686000, 1350000 1686000, 1350000 2406000))', 5070),'4283e3a7-db01-4ddb-9592-e12a361c0b4c'),
('03784645-2ccb-4e77-b391-1ee7e613c3c4','ncrfc','North Central River Forecast Center (NCRFC)',ST_GeomFromText('POLYGON ((-652000 3054000, 1098000 3054000, 1098000 1616000, -652000 1616000, -652000 3054000))', 5070),'4283e3a7-db01-4ddb-9592-e12a361c0b4c'),
('ce33e599-b09b-44f1-9169-f1c0ff804913','nerfc','Northeast River Forecast Center (NERFC)',ST_GeomFromText('POLYGON ((1360000 3042000, 2260000 3042000, 2260000 2160000, 1360000 2160000, 1360000 3042000))', 5070),'4283e3a7-db01-4ddb-9592-e12a361c0b4c'),
('31018b4b-1c64-4d94-ae9f-e2df0979c8c8','nwrfc','Northwest River Forecast Center (NWRFC)',ST_GeomFromText('POLYGON ((-2296000 3506000, -1102000 3506000, -1102000 2190000, -2296000 2190000, -2296000 3506000))', 5070),'4283e3a7-db01-4ddb-9592-e12a361c0b4c'),
('56ed6f77-da5e-4a61-976b-1d13617fe563','ohrfc','Ohio River Forecast Center (OHRFC)',ST_GeomFromText('POLYGON ((610000 2296000, 1490000 2296000, 1490000 1412000, 610000 1412000, 610000 2296000))', 5070),'4283e3a7-db01-4ddb-9592-e12a361c0b4c'),
('75734de7-e02a-4eca-93cb-090521d6625a','wgrfc','West Gulf River Forecast Center (WGRFC)',ST_GeomFromText('POLYGON ((-1206000 1760000, 272000 1760000, 272000 208000, -1206000 208000, -1206000 1760000))', 5070),'4283e3a7-db01-4ddb-9592-e12a361c0b4c');

-- modify the existing SERFC watershed - 724b7228-6174-42c3-b455-a6e4b09f65ee
UPDATE watershed 
    set slug = 'serfc', 
    name = 'Southeast River Forecast Center (SERFC)', 
    geometry = ST_GeomFromText('POLYGON ((630000 1742000, 1834000 1742000, 1834000 272000, 630000 272000, 630000 1742000))', 5070),
    office_id = '4283e3a7-db01-4ddb-9592-e12a361c0b4c'
    WHERE id = '724b7228-6174-42c3-b455-a6e4b09f65ee';

-- remove SERFC office
delete from office where id = 'e303450f-af6a-4272-a262-fdb94f8e3e86';