-- Insert new parameters
INSERT INTO parameter (id, name) VALUES
    ('08abb3a9-cb68-4803-ba45-c4367f74b918','AIRTEMP-MIN'),
    ('83bbf9d3-0af4-4cfd-9f23-6538cf149fa0','AIRTEMP-MAX');

-- update TMIN EARLY
UPDATE product SET parameter_id = '08abb3a9-cb68-4803-ba45-c4367f74b918' 
WHERE id = '62e08d34-ff6b-45c9-8bb9-80df922d0779';

-- update TMAX EARLY
UPDATE product SET parameter_id = '83bbf9d3-0af4-4cfd-9f23-6538cf149fa0' 
WHERE id = '6357a677-5e77-4c37-8aeb-3300707ca885';

-- update TMIN STABLE
UPDATE product SET parameter_id = '08abb3a9-cb68-4803-ba45-c4367f74b918' 
WHERE id = '61fcae9d-cd50-4c00-998b-0a69fc4a2203';

-- UPDATE TMAX STABLE
UPDATE product SET parameter_id = '83bbf9d3-0af4-4cfd-9f23-6538cf149fa0' 
WHERE id = '981aa7ef-3066-404d-8c73-32d347b9d8c9';