
-- basin_product_statistics_enabled
CREATE TABLE IF NOT EXISTS public.basin_product_statistics_enabled (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    basin_id UUID NOT NULL REFERENCES basin(id),
    product_id UUID NOT NULL REFERENCES product(id),
    CONSTRAINT unique_basin_product UNIQUE(basin_id, product_id)
);

-- Basins; Projected to EPSG 5070
CREATE OR REPLACE VIEW v_basin_5070 AS (
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
        FROM basin
    );


-- Function; NOTIFY NEW PRODUCTFILE
CREATE OR REPLACE FUNCTION public.notify_new_productfile ()
  returns trigger
  language plpgsql
AS $$
declare
    channel text := 'cumulus_new_productfile';
begin
	PERFORM (
		WITH payload as (
			SELECT NEW.id AS productfile_id,
				   NEW.product_id  AS product_id,
			       'corpsmap-data' AS s3_bucket,
			       NEW.file        AS s3_key
		)
		SELECT pg_notify(channel, row_to_json(payload)::text)
		FROM payload
	);
	RETURN NULL;
end;
$$;

-- Trigger; NOTIFY NEW PRODUCTFILE ON INSERT
CREATE TRIGGER notify_new_productfile
AFTER INSERT
ON public.productfile
FOR EACH ROW
EXECUTE PROCEDURE public.notify_new_productfile();


GRANT SELECT ON basin_product_statistics_enabled, v_basin_5070 to 'cumulus_reader';
GRANT INSERT,UPDATE,DELETE ON basin_product_statistics_enabled to 'cumulus_writer';
