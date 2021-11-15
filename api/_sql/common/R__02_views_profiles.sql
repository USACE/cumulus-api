-- v_profile
-- create statement here because watershed and watershed_roles
-- tables must exist before creating this view
CREATE OR REPLACE VIEW v_profile AS (
    WITH roles_by_profile AS (
        SELECT profile_id,
               array_agg(UPPER(b.slug || '.' || c.name)) AS roles
        FROM watershed_roles a
        INNER JOIN watershed b ON a.watershed_id = b.id AND NOT b.deleted
        INNER JOIN role      c ON a.role_id    = c.id
        GROUP BY profile_id
    )
    SELECT p.id,
           p.edipi,
           p.username,
           p.email,
           p.is_admin,
           COALESCE(r.roles,'{}') AS roles
    FROM profile p
    LEFT JOIN roles_by_profile r ON r.profile_id = p.id
);

GRANT SELECT ON v_profile TO cumulus_reader;