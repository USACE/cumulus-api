-- remove 'CONUS' from any dss fpart

-- ndfd-conus-qpf-06h
UPDATE product SET dss_fpart = 'NDFD-QPF' WHERE id = '84a64026-0e5d-49ac-a48a-6a83efa2b77c';

-- ndfd-conus-airtemp-01h
UPDATE product SET dss_fpart = 'NDFD' WHERE id = 'b206a00b-9ed6-42e1-a34d-c67d43828810';

-- nbm-co-qpf
UPDATE product SET dss_fpart = 'NBM-QPF' WHERE id = '5317d1c4-c6db-40c2-b527-72f7603be8a0';

-- ndfd-conus-airtemp-03h
UPDATE product SET dss_fpart = 'NDFD' WHERE id = 'dde59007-25ec-4bb4-b5e6-8f0f1fbab853';

-- ndfd-conus-airtemp-06h
UPDATE product SET dss_fpart = 'NDFD' WHERE id = 'f48006a5-ad25-4a9f-9b58-639d75763dd7';

-- nbm-co-airtemp
UPDATE product SET dss_fpart = 'NBM' WHERE id = 'd0c1d6f4-cf5d-4332-a17e-dd1757c99c94';