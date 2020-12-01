

-- Product Group Table
CREATE TABLE IF NOT EXISTS public.product_group (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR NOT NULL
);
-- Product Group Roles
GRANT SELECT ON product_group TO cumulus_reader;
GRANT INSERT,UPDATE,DELETE ON product_group TO cumulus_writer;
-- Product Group Seed Data
INSERT INTO product_group (id, name) VALUES
    ('726039da-2f21-4393-a15c-5f6e7ea41b1f', 'PRECIPITATION'),
    ('d9613031-7cf0-4722-923e-e5c3675a163b', 'TEMPERATURE'),
    ('57bda84f-ecec-4cd7-b3b1-c0c36f838a05', 'SNOW');

-- Modify Product Table
ALTER TABLE product ADD COLUMN is_forecast BOOLEAN;
ALTER TABLE product ADD COLUMN group_id UUID;
-- Modify Existing Product Records
UPDATE product SET is_forecast = false WHERE is_forecast IS NULL;
