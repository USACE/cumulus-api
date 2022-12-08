CREATE TABLE IF NOT EXISTS dss_datatype (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(12) UNIQUE NOT NULL
);

INSERT INTO dss_datatype (id, name) VALUES
    ('b1433fa7-645f-4e3c-b560-29cba59e80c6','INST-VAL'),
    ('cc819bfd-cf3f-446b-93f1-2aff51d7de14','INST-CUM'),
    ('f13182ec-8944-494e-b947-994b189d62f2','PER-AVER'),
    ('392f8984-2e4e-47ea-ae24-dad81d87f662','PER-CUM');

ALTER TABLE product ADD COLUMN dss_datatype_id UUID;
-- Set all product.dss_datatype_id values to 'PER-CUM' for all existing products
UPDATE product SET dss_datatype_id = '392f8984-2e4e-47ea-ae24-dad81d87f662';
-- Set dss_datatype of PER-AVER when parameter is AIRTEMP-MIN or AIRTEMP-MAX
UPDATE product SET dss_datatype_id = 'f13182ec-8944-494e-b947-994b189d62f2' WHERE parameter_id IN ('08abb3a9-cb68-4803-ba45-c4367f74b918', '83bbf9d3-0af4-4cfd-9f23-6538cf149fa0');
-- Set dss_datatype of INST-VAL when temporal_duration = 0
UPDATE product SET dss_datatype_id = 'b1433fa7-645f-4e3c-b560-29cba59e80c6' WHERE temporal_duration = 0;
-- NOT NULL constraint on dss_datatype field
ALTER TABLE product ALTER COLUMN dss_datatype_id SET NOT NULL;
-- Foreign Key Constraint
ALTER TABLE product ADD CONSTRAINT dss_datatype_id_fk FOREIGN KEY (dss_datatype_id) REFERENCES dss_datatype (id);


-- Role cumulus_reader;
-- Grants added to R__01_roles.sql for table dss_datatype
-- Role cumulus_writer
-- Grants added to R__01_roles.sql for table dss_datatype
