# Cumulus Geo Processors

Python package implementation to process incoming grids to Cloud Optimized GeoTIFF (COG).  The `Geoprocessor` is a Python module built into the package and referenced as a plugin using the `pyplugs` package.

## Basic Processor Requirements:

- The Python decorator `@pyplugs.register` defines the `process` method as the plugin
- The plugin name (python filename) has to match the Cumulus Acquirable name
  - Example: `nbm-co-01h` is the acquirable name and the processor name will be `nbm-co-01h.py`
- Processors have to reside under the directory `./geoproc/src/cumulus_geoproc/processors`


## Processor Method

The following is the template for a `process` method in the geoprocessor module (acquirable.py file)

```python
@pyplugs.register
def process(*, src: str, dst: str = None, acquirable: str = None):
    """
    # Grid processor

    __Requires keyword only arguments (*)__

    Parameters
    ----------
    src : str
        path to input file for processing
    dst : str, optional
        path to temporary directory
    acquirable: str, optional
        acquirable slug

    Returns
    -------
    List[dict]
    ```
    {
        "filetype": str,         Matching database acquirable
        "file": str,             Converted file
        "datetime": str,         Valid Time, ISO format with timezone
        "version": str           Reference Time (forecast), ISO format with timezone
    }
    ```
    """
```

## Processor Returns

Processors always return a list of objects as defined below

```python
return [{
    "filetype": str,    Matching database acquirable
    "file": str,        Converted file
    "datetime": str,    Valid Time, ISO format with timezone
    "version": str      Reference Time (forecasts only), ISO format with timezone
}]
```

## Source

The package, tests, license, and single-processor development tools were imported
from [USACE/cumulus-geoproc](https://github.com/USACE/cumulus-geoproc) at commit
[`0a25999b81f69f2922e49b68e323b960fc3f67d3`](https://github.com/USACE/cumulus-geoproc/tree/0a25999b81f69f2922e49b68e323b960fc3f67d3).
The imported `geoproc/` and `geoproc_develop/` files are unchanged from that commit.
The original package license is retained at [geoproc/LICENSE](geoproc/LICENSE).
Upstream commit history remains available in that repository.

Processor changes now belong in this repository. The worker image installs
`./geoproc`, so production, test, and development images use the processors from
that same Cumulus API checkout. The `cumulus_geoproc` import name, worker entrypoint,
and queue message format remain unchanged.

## Processor development and tests

No host GDAL or separate processor repository checkout is needed. From the
Cumulus API repository root:

```bash
# Build the test image and run the unit and reference-data integration tests.
docker compose -f async_geoprocess/docker-compose.tests.yml build geoproc
docker compose -f async_geoprocess/docker-compose.tests.yml run --rm geoproc

# Run only unit tests.
docker compose -f async_geoprocess/docker-compose.tests.yml run --rm geoproc pkg/src/tests/unit -v -p no:cacheprovider

# Open a development shell.
docker compose -f async_geoprocess/docker-compose.tests.yml run --rm --entrypoint bash geoproc
```

For VS Code, open `async_geoprocess/` and choose **Reopen in Container**. Its
devcontainer uses the same test image with an editable processor source mount.

The test Compose service mounts `geoproc/` and uses it via `PYTHONPATH`, so edits
to existing processors are picked up without rebuilding. Rebuild after changing
package dependencies or the Dockerfile. Production builds use the installed
package without these development mounts.

To try a standalone processor, edit `geoproc_develop/processor.py`, place a sample
input file beside it, and run:

```bash
docker compose -f async_geoprocess/docker-compose.tests.yml run --rm --entrypoint python3 geoproc develop/runner.py SAMPLE_FILENAME
```

To use processor changes in the full local Cumulus stack:

```bash
docker compose build geoprocess
docker compose up -d geoprocess
```

## Reference data and CI

Test fixtures remain in
[USACE/cumulus-geoproc-test-data](https://github.com/USACE/cumulus-geoproc-test-data).
The Docker `test` target downloads release `2025-11-04`, matching the original
processor test suite. The archive is about 743 MB; allow additional disk space
for extracted inputs and generated rasters. Update `TEST_DATA_TAG` in
`docker-compose.tests.yml` when adopting a newer fixture release.

The `Test Geoprocessors` workflow runs these tests for pull requests changing
`async_geoprocess/`. Production builds use the default `runtime` target and do
not download test fixtures or install development dependencies.
