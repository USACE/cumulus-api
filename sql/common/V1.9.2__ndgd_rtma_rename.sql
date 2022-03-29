
-- Airtemp
UPDATE product 
    SET "label" = 'RTMA', 
    dss_fpart = 'NDGD-RTMA', 
    description = 'National Digital Guidance Database (NDGD) Real-Time Mesoscale Analysis (RTMA) CONUS Air Temperature'
    WHERE id = '5e6ca7ed-007d-4944-93aa-0a7a6116bdcd';

-- Precip
UPDATE product 
    SET "label" = 'RTMA', 
    dss_fpart = 'NDGD-RTMA', 
    description = 'National Digital Guidance Database (NDGD) Real-Time Mesoscale Analysis (RTMA) CONUS Precipitation'
    WHERE id = '1ba5498c-d507-4c82-a80b-9b0af952b02f';