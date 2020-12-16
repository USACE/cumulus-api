CREATE OR REPLACE VIEW v_download AS (
        SELECT d.id AS id,
            d.datetime_start AS datetime_start,
            d.datetime_end AS datetime_end,
            d.progress AS progress,
            d.file AS file,
            d.processing_start AS processing_start,
            d.processing_end AS processing_end,
            d.status_id AS status_id,
            d.watershed_id AS watershed_id,
            s.name AS status,
            dp.product_id AS product_id
        FROM download d
            INNER JOIN download_status s ON d.status_id = s.id
            INNER JOIN watershed w on d.watershed_id = w.id
            INNER JOIN (
                SELECT array_agg(id) as product_id,
                    download_id
                FROM download_product
                GROUP BY download_id
            ) dp ON d.id = dp.download_id
    );

CREATE OR REPLACE VIEW v_watershed AS (
    SELECT w.id,
           w.slug,
           w.name,
           ST_XMin(w.geometry) AS x_min,
           ST_Ymin(w.geometry) AS y_min,
           ST_XMax(w.geometry) AS x_max,
           ST_YMax(w.geometry) AS y_max,
           COALESCE(ag.area_groups, '{}') AS area_groups,
           f.symbol AS office_symbol
	FROM   watershed w
	LEFT JOIN (
		SELECT array_agg(id) as area_groups, watershed_id
		FROM area_group
		GROUP BY watershed_id
	) ag ON ag.watershed_id = w.id
    LEFT JOIN office f ON w.office_id = f.id
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