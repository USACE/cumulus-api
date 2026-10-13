"""

"""

import json
from pathlib import Path


file = Path(
    "/workspaces/cumulus-geoproc/src/tests/integration/fixtures/test_products.json"
)

fixtures_path = Path("/workspaces/cumulus-geoproc/cumulus-geoproc-test-data/fixtures")

def json_config_per_product():
    with file.open("r", encoding="utf-8") as fptr:
        jj = json.load(fptr)
        for j in jj:
            fixture_path = (fixtures_path / j["plugin"] / j["plugin"]).with_suffix(".json")

            with fixture_path.open("w", encoding="utf-8") as fxtr:
                fxtr.write(json.dumps(j, indent=4))
