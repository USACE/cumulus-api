-- extensions
CREATE extension IF NOT EXISTS "uuid-ossp";


-- drop tables if they already exist
drop table if exists
    public.area_group_product_statistics_enabled
    CASCADE;

-- area_group_product_statistics_enabled
CREATE TABLE IF NOT EXISTS public.area_group_product_statistics_enabled (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    area_group_id UUID NOT NULL REFERENCES area_group(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES product(id) ON DELETE CASCADE,
    CONSTRAINT unique_area_group_product UNIQUE(area_group_id, product_id)
);
