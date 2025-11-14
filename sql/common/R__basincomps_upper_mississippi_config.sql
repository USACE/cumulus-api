-- Repeatable migration: Configure Upper Mississippi basin for BasinComps
-- This will run whenever the file changes

DO $$
DECLARE
    v_wpc_id UUID;
    v_ndfd_id UUID;
    v_product_ids UUID[];
    v_missing_products TEXT := '';
BEGIN
    -- Find WPC QPF product
    SELECT id INTO v_wpc_id
    FROM product
    WHERE slug = 'wpc-qpf-2p5km'
    LIMIT 1;

    -- Find NDFD QPF 6hr product
    SELECT id INTO v_ndfd_id
    FROM product
    WHERE slug = 'ndfd-conus-qpf-06h'
    LIMIT 1;

    -- Check which products are missing
    IF v_wpc_id IS NULL THEN
        v_missing_products := v_missing_products || 'wpc-qpf-2p5km ';
    END IF;

    IF v_ndfd_id IS NULL THEN
        v_missing_products := v_missing_products || 'ndfd-conus-qpf-06h ';
    END IF;

    IF v_missing_products != '' THEN
        -- Some products not found - log warning and skip configuration
        RAISE WARNING 'Products not found: %. Skipping Upper Mississippi configuration. Please add the products and re-run migrations.', v_missing_products;
    ELSE
        -- All products found - create the configuration
        v_product_ids := ARRAY[v_wpc_id, v_ndfd_id];

        INSERT INTO basincomps_shapefile_config (
            config_name,
            description,
            shapefile_path,
            product_ids,
            enabled
        )
        VALUES (
            'upper-mississippi',
            'Upper Mississippi River watershed basins - Test configuration',
            '/app/config/upper_mississippi.shp',
            v_product_ids,
            true
        )
        ON CONFLICT (config_name)
        DO UPDATE SET
            description = EXCLUDED.description,
            shapefile_path = EXCLUDED.shapefile_path,
            product_ids = EXCLUDED.product_ids,
            enabled = EXCLUDED.enabled,
            updated_at = NOW();

        RAISE NOTICE 'Upper Mississippi configuration created successfully with wpc-qpf-2p5km and ndfd-conus-qpf-06h';
    END IF;
END $$;
