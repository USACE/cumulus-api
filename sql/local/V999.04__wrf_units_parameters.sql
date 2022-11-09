-- Insert new parameters
INSERT INTO parameter (id, name) VALUES
    ('c680d0a3-909e-4046-bbae-18127ad589a6','PRESSURE'),
    ('90cf9fe0-ded9-45a8-abc6-78aa25f3fde3','PRESSURE-VAPOR'),
    ('8328aa49-2c7d-454c-b7e7-d9b2ffeba728','PRESSURE-SURFACE'),
    ('90208e7b-bc6f-47dd-a704-0be2423f9222','VELOCITY'),
    ('c563cb29-b7b9-4f73-b1c3-a87d931ff5e0','VELOCITY-V10METER'),
    ('2d03d408-dd0e-4b6e-8944-e453c63222a7','VELOCITY-U10METER'),
    ('99e72720-70d2-4d56-aa0e-4f5bcbabe6d2','IRRADIANCE'),
    ('14dc8407-f63a-4237-8251-5ef1746c3d89','IRRADIANCE-SHORTWAVE'),
    ('6f3efef3-6d6c-4378-94e3-0d7be7321707','IRRADIANCE-LONGWAVE'),
    ('8f616a56-63dc-45fd-854a-67abd21f7f2f','HUMIDITY'),
    ('c2c25499-1bc0-4c92-b429-446eaaf37768','HUMIDITY-RELATIVE'),
    ('5c993bde-6024-45ac-9b54-d4b87fac3b50','TEMPERATURE'),
    ('ca11ed97-02b9-4a44-9280-70c08bc0d5f9','TEMPERATURE-GROUND'),
    ('1997ea14-9908-46e5-8d59-0ec7b1b7fc5d','TEMPERATURE-DEWPOINT'),
    ('37281336-ac37-4824-b83f-bcbc37a64daf','AIRTEMP-2METER')
ON CONFLICT (id) DO NOTHING;

-- Insert new units
INSERT INTO unit (id, name, abbreviation) VALUES
    ('d5e7b710-f759-4eef-a0eb-d3148d81c43c','METER PER SEC','m/s'),
    ('bc613cae-602f-4973-b496-34c503afa666','KILOPASCAL','kPa'),
    ('c32186a9-28c8-4fda-84cf-a107d4fd40b4','HECTOPASCAL','hPa'),
    ('880d70f4-d17a-44ba-8f1c-8ff58a87ef89','WATT PER M2','W/m2'),
    ('5dd42877-0967-432e-9d84-a0b7239b4647','PERCENT','%')
ON CONFLICT (id) DO NOTHING;
