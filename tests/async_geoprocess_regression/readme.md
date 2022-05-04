# Geoprocess Regression Tests

## Setup
- Set docker-compose.yml arguments `GIT_REPO_URL` and `GIT_BRANCH` to your new proposed branch.

## How to use
1) Start cumulus-api (using a production - stable/develop branch) including minio and airflow
2) Turn on DAG(s) for the product(s) you wish to test. _this will write to minio and create db records_
3) When the geoprocessor is done with pending work, run the `async_geoprocess_regression` by using `docker compose up --build` while in the async_geoprocess_regression dir.

## Concepts
- `Golden` refers to a product that is generated from known good code.

## What will happen
The tester.py script will:
1) Get all the acquirablefiles records from the database (via API call)
2) Build messages and execute the geoprocess `handle_message()` for each, resulting in tifs placed in `/cumulus/products/{product_slug}/`
3) Get productfiles from the database (via API) and download records from minio to `/cumulus/products_golden/{product_slug}/`
4) Use `gdalcompare.find_diff()` to compare the golden vs new file.
5) Check validity of new A Cloud Optimized Geotif (COG) tif file.
6) Display results to standard output.

## Known Issues
- SNODAS may not work correctly
- Renaming the output tif between branches may cause errors