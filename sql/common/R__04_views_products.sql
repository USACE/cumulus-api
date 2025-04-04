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
		SELECT product_series_id             AS product_series_id,
               array_agg(tag_id ORDER BY tag_id::VARCHAR)  AS tags
	    FROM product_tags
	    GROUP BY product_series_id
	)
	SELECT a.id                              AS id,
           a.slug                            AS slug,
           CONCAT(
               UPPER(s.slug), ' ', 
               (CASE WHEN LENGTH(ps.label) > 1
                     THEN CONCAT(ps.label, ' ')
                     ELSE ''
                END), 
                p.name, ' ',
                a.temporal_resolution/60/60, 'hr'
           )                                 AS name,
           ps.label                          AS label,
           a.temporal_resolution             AS temporal_resolution,
           a.temporal_duration               AS temporal_duration,
           d.id								 AS dss_datatype_id,
           d.name                            AS dss_datatype,
           ps.dss_fpart                      AS dss_fpart,
           ps.description                    AS description,
           ps.suite_id                       AS suite_id,
           s.name                            AS suite,
           COALESCE(t.tags, '{}')            AS tags,
           p.id                              AS parameter_id,
           p.name                            AS parameter,
           u.id                              AS unit_id,
           u.name                            AS unit,
           pf.after                          AS after,
           pf.before                         AS before,
           COALESCE(pf.productfile_count, 0) AS productfile_count,
           pf.last_forecast_version          AS last_forecast_version,
           a.product_series_id               AS product_series_id
	FROM product a
	JOIN product_series ps ON ps.id = a.product_series_id 
	JOIN unit u ON u.id = ps.unit_id
	JOIN parameter p ON p.id = ps.parameter_id
    JOIN suite s ON s.id = ps.suite_id
    JOIN dss_datatype d ON d.id = ps.dss_datatype_id
	LEFT JOIN tags_by_product t ON t.product_series_id = ps.id
    LEFT JOIN (
        SELECT product_id     AS product_id,
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

-- v_product_series
CREATE OR REPLACE VIEW v_product_series AS (
    WITH tags_by_product AS (
		SELECT product_series_id             AS product_series_id,
               array_agg(tag_id ORDER BY tag_id::VARCHAR)  AS tags
	    FROM product_tags
	    GROUP BY product_series_id
	), temporal_stats AS (
        SELECT product_series_id,
            CASE
                WHEN COUNT(product_series_id) = 1 THEN MAX(temporal_resolution)
                ELSE NULL
            END AS temporal_resolution,
            CASE
                WHEN COUNT(product_series_id) = 1 THEN MAX(temporal_duration)
                ELSE NULL
            END AS temporal_duration
        FROM product
        GROUP BY product_series_id
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
                (CASE WHEN ts.temporal_resolution IS NOT NULL
                      THEN CONCAT(ts.temporal_resolution/60/60, 'hr')
                      ELSE ''
                END)
           )                                 AS name,
           a.label                           AS label,
           ts.temporal_resolution            AS temporal_resolution,
           ts.temporal_duration              AS temporal_duration,
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
           pf.after                          AS after,
           pf.before                         AS before,
           COALESCE(pf.productfile_count, 0) AS productfile_count,
           pf.last_forecast_version          AS last_forecast_version
	FROM product_series a
	JOIN unit u ON u.id = a.unit_id
	JOIN parameter p ON p.id = a.parameter_id
    JOIN suite s ON s.id = a.suite_id
    JOIN dss_datatype d ON d.id = a.dss_datatype_id
	LEFT JOIN tags_by_product t ON t.product_series_id = a.id
    LEFT JOIN temporal_stats ts ON ts.product_series_id = a.id
    LEFT JOIN (
        SELECT p.product_series_id AS product_series_id,
                COUNT(pf.id)       AS productfile_count,
                MIN(pf.datetime)   AS after,
                MAX(pf.datetime)   AS before,
                NULLIF(max(pf."version"),'1111-11-11T11:11:11.11Z') AS last_forecast_version
        FROM productfile pf
        LEFT JOIN product p ON p.id = product_id
        GROUP BY product_series_id
    ) AS pf ON pf.product_series_id = a.id
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
    v_product_series,
    v_productfile,
    v_product_status
TO cumulus_reader;