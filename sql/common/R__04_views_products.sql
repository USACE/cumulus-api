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
               array_agg(tag_id)  AS tags
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
           a.dss_fpart                       AS dss_fpart,
           a.description                     AS description,
           a.suite_id                        AS suite_id,
           s.name                            AS suite,
           COALESCE(t.tags, '{}')            AS tags,
           p.id                              AS parameter_id,
           p.name                            AS parameter,
           u.id                              AS unit_id,
           u.name                            AS unit,
           pf.after                          AS after,
           pf.before                         AS before,
           COALESCE(pf.productfile_count, 0) AS productfile_count,
           pf.last_forecast_version          AS last_forecast_version
	FROM product a
	JOIN unit u ON u.id = a.unit_id
	JOIN parameter p ON p.id = a.parameter_id
    JOIN suite s ON s.id = a.suite_id
	LEFT JOIN tags_by_product t ON t.product_id = a.id
    LEFT JOIN (
        SELECT product_id    AS product_id,
                COUNT(id)     AS productfile_count,
                MIN(datetime) AS after,
                MAX(datetime) AS before,
                NULLIF(max(productfile."version"),'1111-11-11T11:11:11.11Z') AS last_forecast_version
        FROM productfile
        GROUP BY product_id
    ) AS pf ON pf.product_id = a.id
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
        max_date AS lastest_product_datetime,
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