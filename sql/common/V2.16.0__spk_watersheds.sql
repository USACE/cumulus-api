-- extent to polygon reference order - simple 4 point extents

-- Updates to existing watersheds
-- Sacramento River
UPDATE watershed 
    set geometry = ST_GeomFromText('POLYGON ((-2291054 1967530, -1966382 1967530, -1966382 2415240, -2291054 2415240, -2291054 1967530))', 5070)
    WHERE id = 'e837f3e1-de8f-4ead-a38a-30d290972cea';

-- -- San Joaquin River
UPDATE watershed
    set geometry = ST_GeomFromText('POLYGON ((-2234785 1730791, -1972021 1730791, -1972021 2024267, -2234785 2024267, -2234785 1730791))',5070)
    WHERE id = '7b550f3a-91c3-4136-9595-d6e5acf1b7fa';

-- -- Tulare River
UPDATE watershed
    set geometry = ST_GeomFromText('POLYGON ((-2191241 1535861, -1931749 1535861, -1931749 1832457, -2191243 1832457, -2191243 1535861))',5070)
    WHERE id = 'e627a104-4bba-45d1-a824-3b0bfdbe4bc4';

-- New Watersheds
-- Upper Sacramento River
-- Northern Sierra Sacramento River
-- Lower Sacramento River
-- Upper San Joaquin River
-- Lower San Joaquin RIver
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
    ('7b97b65c-a2ae-40e5-8e7f-2036f6f20b0a','upper-sacramento-river','Upper Sacramento River',ST_GeomFromText('POLYGON ((-2291054 2039423, -1966382 2039423, -1966382 2415240, -2291054 2415240, -2291054 2039423))', 5070),'df64a2de-91a2-4e6c-85c9-53d3d03f6794'),
    ('190196e9-609e-4658-af33-689521a8a083','northern-sierra-sacramento-river','Northern Sierra Sacramento River',ST_GeomFromText('POLYGON ((-2173855 1994301, -2020110 1994301, -2020110 2227593, -2173855 2227593, -2173855 1994301))', 5070),'df64a2de-91a2-4e6c-85c9-53d3d03f6794'),
    ('64a02cf1-0c24-4e61-ad55-e40f246eece0','lower-sacramento-river','Lower Sacramento River',ST_GeomFromText('POLYGON ((-2271505 1967530, -2118652 1967530, -2118652 2192030, -2271504 2192030, -2271505 1967530))', 5070),'df64a2de-91a2-4e6c-85c9-53d3d03f6794'),
    ('55092e94-3be4-454f-bfc1-509b7b509a2a','upper-san-joaquin-river','Upper San Joaquin River',ST_GeomFromText('POLYGON ((-2193880 1730791, -1972021 1730791, -19720217 1882718, -2193880 1882718, -2193880 1730791))', 5070),'df64a2de-91a2-4e6c-85c9-53d3d03f6794'),
    ('7e7a6cfd-f872-45fc-ba7a-a954c2f67d34','lower-san-joaquin-river','Lower San Joaquin River',ST_GeomFromText('POLYGON ((-2234785 1811586, -2000884 1811586, -2000884 2024267, -2234785 2024267, -2234785 1811586))', 5070),'df64a2de-91a2-4e6c-85c9-53d3d03f6794');
