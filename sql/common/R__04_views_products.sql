-- Always re-apply when running migrations: ${flyway:timestamp}
-- v_acquirablefile
CREATE OR REPLACE VIEW v_acquirablefile AS (
    SELECT a.id           AS acquirable_id,
           a.name         AS acquirable_name,
           a.slug         AS acquirable_slug,
           f.id           AS id,
           f.datetime     AS datetime,
           f.file         AS file,
           f.create_date  AS create_date,
           f.process_date AS process_date
    FROM acquirablefile f
    LEFT JOIN acquirable a ON a.id = f.acquirable_id
);

-- v_product
CREATE OR REPLACE VIEW v_product AS (
    WITH tags_by_product AS (
		SELECT product_id         AS product_id,
               array_agg(tag_id ORDER BY tag_id::VARCHAR)  AS tags
	    FROM product_tags
	    GROUP BY product_id
	)
	SELECT a.id                              AS id,
           a.slug                            AS slug,
           CONCAT(
               UPPER(s.slug), ' ', 
               (CASE WHEN LENGTH(a.label) > 1
                     THEN CONCAT(a.label, ' ')
                     ELSE ''
                END), 
                p.name, ' ',
                a.temporal_resolution/60/60, 'hr'
           )                                 AS name,
           a.label                           AS label,
           a.temporal_resolution             AS temporal_resolution,
           a.temporal_duration               AS temporal_duration,
           d.id								 AS dss_datatype_id,
           d.name                            AS dss_datatype,
           a.dss_fpart                       AS dss_fpart,
           a.description                     AS description,
           a.suite_id                        AS suite_id,
           s.name                            AS suite,
           COALESCE(t.tags, '{}')            AS tags,
           p.id                              AS parameter_id,
           p.name                            AS parameter,
           u.id                              AS unit_id,
           u.name                            AS unit,
           -- The productfile date range and count, as one correlated lookup per product rather
           -- than an aggregate over the table: product has ~100 rows, so ~100 indexed lookups
           -- beat one scan of a multi-million-row table.
           --
           -- These depend on productfile_product_id_datetime_idx (product_id, datetime). It is
           -- what collapses each min()/max() to an ORDER BY ... LIMIT 1 index hit -- Postgres
           -- applies that rewrite to ungrouped aggregates only -- and what makes the count an
           -- index-only scan. Without it there is no way to return datetime in order for one
           -- product (unique_product_version_datetime is (product_id, version, datetime), so it
           -- orders by version first) and each subquery falls back to scanning the product's whole
           -- history. See V2.68.0__productfile_product_datetime_index.sql.
           (SELECT min(f.datetime) FROM productfile f WHERE f.product_id = a.id) AS after,
           (SELECT max(f.datetime) FROM productfile f WHERE f.product_id = a.id) AS before,
           (SELECT count(*) FROM productfile f WHERE f.product_id = a.id) AS productfile_count,
           -- Latest forecast issue time, NULL for observed products. Observed rows carry a
           -- year-1111 sentinel in version; production holds several distinct sentinel values
           -- (1111-11-04 11:04:09.11+00 on most rows, plus 1111-11-11 11:11:11.11+00 and
           -- 1111-11-03 23:52:58+00), so they are excluded by range rather than by matching one
           -- literal. Nothing below 1900 is a real issue time. The range also uses
           -- unique_product_version_datetime's (product_id, version) prefix.
           (SELECT max(f.version) FROM productfile f
             WHERE f.product_id = a.id
               AND f.version >= '1900-01-01'::timestamptz) AS last_forecast_version
	FROM product a
	JOIN unit u ON u.id = a.unit_id
	JOIN parameter p ON p.id = a.parameter_id
    JOIN suite s ON s.id = a.suite_id
    JOIN dss_datatype d ON d.id = a.dss_datatype_id
	LEFT JOIN tags_by_product t ON t.product_id = a.id
    WHERE NOT a.deleted
    order by name
);

-- v_productfile
CREATE OR REPLACE VIEW v_productfile AS (
    SELECT p.id           AS product_id,
           p.name         AS product_name,
           p.slug         AS product_slug,
           f.id           AS id,
           f.datetime     AS datetime,
           f.file         AS file,
           f.version      AS version
    FROM productfile f
    LEFT JOIN v_product p ON p.id = f.product_id
);

-- v_product_status
CREATE OR REPLACE VIEW v_product_status AS (
    WITH pf_date AS (
        SELECT pf.product_id, max(pf.datetime) AS max_date
            FROM cumulus.productfile pf
            WHERE DATE_PART('year', pf.version::date) = '1111'
            GROUP BY pf.product_id
        UNION
        SELECT pf.product_id, max(pf.version) AS max_date
            FROM cumulus.productfile pf
            WHERE DATE_PART('year', pf.version::date) != '1111'
            GROUP BY pf.product_id 
    )
    SELECT 
        p.slug,
        max_date AS latest_product_datetime,
        p.acceptable_timedelta,
        DATE_TRUNC('minute', (CURRENT_TIMESTAMP - max_date)) AS actual_timedelta,
        CASE 
            WHEN (p.acceptable_timedelta IS NOT NULL) 
            AND max_date >= DATE_TRUNC('minute', (CURRENT_TIMESTAMP - p.acceptable_timedelta)) THEN TRUE 
            ELSE FALSE 
        END AS is_current
    FROM cumulus.product p 
    LEFT JOIN pf_date md ON md.product_id = p.id
    ORDER BY p.slug
);



GRANT SELECT ON
    v_acquirablefile,
    v_product,
    v_productfile,
    v_product_status
TO cumulus_reader;