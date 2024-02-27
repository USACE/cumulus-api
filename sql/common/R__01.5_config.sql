INSERT INTO config (config_name, config_value) VALUES
('write_to_bucket', '${WRITE_TO_BUCKET}') ON CONFLICT DO NOTHING;