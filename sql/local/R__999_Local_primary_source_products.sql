-- Define the list of products that should have the Primary Source tag
-- To add more products in the future, simply add their UUIDs to this array
WITH primary_source_products AS (
    SELECT unnest(ARRAY[
        -- NCEP STAGE4 MOSAIC QPE PRECIP 1hr
        '16d4c494-63e6-4d33-b2da-7be065a6776b'::UUID,
        -- WPC QPF PRECIP 6hr
        '0ac60940-35c2-4c0d-8a3b-49c20e455ff5'::UUID,
        -- NDGD RTMA AIRTEMP 1hr
        '5e6ca7ed-007d-4944-93aa-0a7a6116bdcd'::UUID,
        -- NBM QTF AIRTEMP 1hr
        'd0c1d6f4-cf5d-4332-a17e-dd1757c99c94'::UUID,
        -- NBM QTF AIRTEMP 3hr
        'f43cb3b8-221a-4ff0-aaa6-5937e54323b6'::UUID,
        -- NBM QTF AIRTEMP 6hr
        '7e5c7acf-7d2b-4d02-a582-7ddf9b2e3700'::UUID,
        -- SNODAS-INTERPOLATED SWE 24hr
        '517369a5-7fe3-4b0a-9ef6-10f26f327b26'::UUID,
        -- SNODAS-INTERPOLATED COLD CONTENT 24hr
        '33407c74-cdc2-4ab2-bd9a-3dff99ea02e4'::UUID
    ]) AS product_id
)
-- Insert product-tag relationships, ignoring any that already exist
INSERT INTO product_tags (product_id, tag_id)
SELECT
    psp.product_id,
    '8a7f4e6b-3c2d-4a9f-b1e5-9d8c7a6f5e4d'::UUID AS tag_id
FROM primary_source_products psp
WHERE EXISTS (SELECT 1 FROM product WHERE id = psp.product_id)
ON CONFLICT (tag_id, product_id) DO NOTHING;

-- Remove the Primary Source tag from products that are no longer in the list
DELETE FROM product_tags
WHERE tag_id = '8a7f4e6b-3c2d-4a9f-b1e5-9d8c7a6f5e4d'::UUID
AND product_id NOT IN (
    SELECT unnest(ARRAY[
        '16d4c494-63e6-4d33-b2da-7be065a6776b'::UUID,
        '0ac60940-35c2-4c0d-8a3b-49c20e455ff5'::UUID,
        '5e6ca7ed-007d-4944-93aa-0a7a6116bdcd'::UUID,
        'd0c1d6f4-cf5d-4332-a17e-dd1757c99c94'::UUID,
        'f43cb3b8-221a-4ff0-aaa6-5937e54323b6'::UUID,
        '7e5c7acf-7d2b-4d02-a582-7ddf9b2e3700'::UUID,
        '517369a5-7fe3-4b0a-9ef6-10f26f327b26'::UUID,
        '33407c74-cdc2-4ab2-bd9a-3dff99ea02e4'::UUID
    ])
);