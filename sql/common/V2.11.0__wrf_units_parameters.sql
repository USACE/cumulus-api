-- Insert new parameters
INSERT INTO parameter (id, name) VALUES
    ('f1d2fee8-ac86-499f-83be-b15bcde43d76','PRESSURE'),
    ('a4cbef84-fd47-415a-910c-d143dcb20ba4','VELOCITY'),
    ('7586a687-7f31-4fa0-8447-eb31d199a05a','IRRADIANCE'),
    ('8dd6420d-e624-45c0-90ed-b5ec3756d2f1','HUMIDITY'),
    ('256e12c8-93d4-4a79-b3ac-6259426a189a', 'TEMPERATURE');

-- Insert new units
INSERT INTO unit (id, name, abbreviation) VALUES
    ('d5e7b710-f759-4eef-a0eb-d3148d81c43c','METER PER SEC','m/s'),
    ('bc613cae-602f-4973-b496-34c503afa666','KILOPASCAL','kPa'),
    ('c32186a9-28c8-4fda-84cf-a107d4fd40b4','HECTOPASCAL','hPa'),
    ('880d70f4-d17a-44ba-8f1c-8ff58a87ef89','WATT PER M2','W/m2'),
    ('5dd42877-0967-432e-9d84-a0b7239b4647','PERCENT','%');
