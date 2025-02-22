-- create a product_series table containing product series that can be comprised
-- of a single or multiple products of varying temporal resolution and duration

CREATE TABLE IF NOT EXISTS product_series (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    slug VARCHAR(120) UNIQUE NOT NULL,
    label VARCHAR(40) NOT NULL DEFAULT '',
    dss_fpart VARCHAR(40),
    parameter_id UUID NOT NULL REFERENCES parameter (id),
    description TEXT NOT NULL DEFAULT '',
    unit_id UUID NOT NULL REFERENCES unit (id),
    suite_id UUID NOT NULL REFERENCES suite (id),
    dss_datatype_id UUID NOT NULL REFERENCES dss_datatype (id),
    deleted BOOLEAN NOT NULL DEFAULT false
);