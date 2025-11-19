-- This migration creates and maintains the "Primary Source" tag

-- Create the Primary Source tag if it doesn't exist
INSERT INTO tag (id, name, description, color)
VALUES (
    '8a7f4e6b-3c2d-4a9f-b1e5-9d8c7a6f5e4d',
    'Primary Source',
    'Products designated as primary data sources for their respective data types',
    '9333EA'  -- Purple color
)
ON CONFLICT (id) DO UPDATE
SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    color = EXCLUDED.color;
