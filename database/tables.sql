-- office
CREATE TABLE IF NOT EXISTS public.office (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    symbol VARCHAR(120) UNIQUE NOT NULL,
    name VARCHAR(120) UNIQUE NOT NULL
);

-- basin
CREATE TABLE IF NOT EXISTS public.basin (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    slug VARCHAR(240) UNIQUE NOT NULL,
    name VARCHAR(120) NOT NULL,
    geometry geometry,
    x_min INTEGER NOT NULL,
    y_min INTEGER NOT NULL,
    x_max INTEGER NOT NULL,
    y_max INTEGER NOT NULL,
    office_id UUID NOT NULL REFERENCES office (id)
);

-- parameter
CREATE TABLE IF NOT EXISTS public.parameter (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(120) UNIQUE NOT NULL
);

-- unit
CREATE TABLE IF NOT EXISTS public.unit (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(120) UNIQUE NOT NULL
);

-- product
CREATE TABLE IF NOT EXISTS public.product (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(120) NOT NULL,
    temporal_duration INTEGER NOT NULL,
    temporal_resolution INTEGER NOT NULL,
    dss_fpart VARCHAR(40),
    is_realtime BOOLEAN,
    parameter_id UUID NOT NULL REFERENCES parameter (id),
    unit_id UUID NOT NULL REFERENCES unit (id)
);

-- productfile
CREATE TABLE IF NOT EXISTS public.productfile (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    datetime TIMESTAMPTZ NOT NULL,
    file VARCHAR(1200) NOT NULL,
    product_id UUID REFERENCES product (id)
);

-- token
CREATE TABLE IF NOT EXISTS public.token (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    issued TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    hash VARCHAR(240) NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE
);

-- acquirable
CREATE TABLE IF NOT EXISTS public.acquirable (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(120) NOT NULL,
    schedule VARCHAR(120)
);

-- acquisition
CREATE TABLE IF NOT EXISTS public.acquisition (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    datetime TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- acquirable_acquisition
CREATE TABLE IF NOT EXISTS public.acquirable_acquisition (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    acquisition_id UUID REFERENCES acquisition (id),
    acquirable_id UUID REFERENCES acquirable (id)
);
