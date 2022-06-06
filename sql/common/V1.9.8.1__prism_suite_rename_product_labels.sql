-- remove "EARLY" from suite name
--add description
UPDATE suite 
SET slug = 'prism', 
name = 'Parameter-elevation Regressions on Independent Slopes Model (PRISM)',
description = 'The PRISM Climate Group gathers climate observations from a wide range of monitoring networks, applies sophisticated quality control measures, and develops spatial climate datasets to reveal short- and long-term climate patterns. The resulting datasets incorporate a variety of modeling techniques and are available at multiple spatial/temporal resolutions, covering the period from 1895 to the present'
where id = '9252e4e6-18fa-4a33-a3b6-6f99b5e56f13';

-- Add STABLE to label
UPDATE product set label = 'STABLE TMAX' where id = '981aa7ef-3066-404d-8c73-32d347b9d8c9';
UPDATE product set label = 'STABLE TMIN' where id = '61fcae9d-cd50-4c00-998b-0a69fc4a2203';
UPDATE product set label = 'STABLE PPT' where id = 'b86e81b0-a860-46b1-bbc8-23b02234a4d2';

-- Add EARLY to label
UPDATE product set label = 'EARLY TMAX' where id = '6357a677-5e77-4c37-8aeb-3300707ca885';
UPDATE product set label = 'EARLY TMIN' where id = '62e08d34-ff6b-45c9-8bb9-80df922d0779';
UPDATE product set label = 'EARLY PPT' where id = '64756f41-75e2-40ce-b91a-fda5aeb441fc';