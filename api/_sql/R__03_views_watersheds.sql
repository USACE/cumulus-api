
CREATE OR REPLACE VIEW v_watershed AS (
    SELECT w.id,
           w.slug,
           w.name,
           w.geometry AS geometry,
           COALESCE(ag.area_groups, '{}') AS area_groups,
           f.symbol AS office_symbol
	FROM   watershed w
	LEFT JOIN (
		SELECT array_agg(id) as area_groups, watershed_id
		FROM area_group
		GROUP BY watershed_id
	) ag ON ag.watershed_id = w.id
    LEFT JOIN office f ON w.office_id = f.id
	WHERE NOT w.deleted
);


-- Basins; Projected to EPSG 5070
CREATE OR REPLACE VIEW v_area_5070 AS (
	SELECT id,
		slug,
		name,
			ST_SnapToGrid(
				ST_Transform(
					geometry,
					'+proj=aea +lat_0=23 +lon_0=-96 +lat_1=29.5 +lat_2=45.5 +x_0=0 +y_0=0 +datum=NAD83 +units=us-ft +no_defs',
					5070
				),
				1
			) AS geometry
	FROM area
);

-- v_watershed_roles
CREATE OR REPLACE VIEW v_watershed_roles AS (
    SELECT a.id,
           a.profile_id,
           b.edipi,
           b.username,
           b.email,
           b.is_admin,
           c.id AS watershed_id,
           r.id   AS role_id,
           r.name AS role,
           UPPER(c.slug || '.' || r.name) AS rolename
    FROM watershed_roles a
    INNER JOIN profile b ON b.id = a.profile_id
    INNER JOIN watershed c ON c.id = a.watershed_id AND NOT c.deleted
    INNER JOIN role    r ON r.id = a.role_id
    ORDER BY username, role
);

GRANT SELECT ON
    v_area_5070,
    v_watershed,
    v_watershed_roles
TO cumulus_reader;