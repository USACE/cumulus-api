from genericpath import exists
import requests
import traceback
import os, sys
import shutil
from tempfile import TemporaryDirectory
import pathlib
import validate_cloud_optimized_geotiff
from datetime import datetime, timedelta

# import worker
from collections import namedtuple

# from worker import handle_message
from cumulus_geoproc.geoprocess import handler
from cumulus_geoproc.utils.boto import s3_download_file

from osgeo_utils import gdalcompare

now = datetime.now()
FILES_START_DATE = (now - timedelta(days=10)).strftime("%Y%m%d")
FILES_START_END = (now + timedelta(days=10)).strftime("%Y%m%d")


def get_acquirables():
    # Get all acquirables currently in local database
    r = requests.get(f"http://api/acquirables")
    return r.json()


def get_acquirablefiles(acquirables):
    # Get all acquirable files currently in local database
    acquirable_db_records = []
    for a in acquirables:
        # print(a["id"], " - ", a["slug"])
        r = requests.get(
            f"http://api/acquirables/{a['id']}/files?after={FILES_START_DATE}&before={FILES_START_END}&key=appkey"
        )
        # print(len(r.json()))
        if r.status_code == 200 and len(r.json()) > 0:
            acquirable_db_records.extend(r.json())
    return acquirable_db_records


def get_products():
    # Get all products currently in local database
    r = requests.get(f"http://api/products")
    return r.json()


def get_productfiles(products):
    # Get all product files currently in local database
    productfile_db_records = []
    for p in products:
        # print(p["id"], " - ", p["slug"])
        r = requests.get(
            f"http://api/products/{p['id']}/files?after={FILES_START_DATE}&before={FILES_START_END}&key=appkey"
        )
        # print(len(r.json()))
        if r.status_code == 200 and len(r.json()) > 0:
            productfile_db_records.extend(r.json())
    return productfile_db_records


def lookup_product_slug_by_acquirablefile_id(acquirablefile_id):
    productfiles = get_productfiles(get_products())
    # print(productfiles)
    for p in productfiles:
        if p["acquirablefile_id"] == acquirablefile_id:
            # return the slug (cheat and grab it from file)
            return p["file"].split("/")[-2]


BUCKET = "castle-data-develop"
print(f"Getting db records in time window {FILES_START_DATE} to {FILES_START_END}")
acquirablefiles = get_acquirablefiles(get_acquirables())
products_dir = "/tmp/cumulus/products"

for af in acquirablefiles:
    acquirable_slug = af["file"].split("/")[-2]
    payload = {
        "geoprocess": "incoming-file-to-cogs",
        "geoprocess_config": {
            "acquirablefile_id": af["id"],
            "acquirable_id": af["acquirable_id"],
            "acquirable_slug": acquirable_slug,
            "bucket": "castle-data-develop",
            "key": af["file"],
        },
    }

    # ---------------------------------------------
    # Create the tiffs on local disk for analysis
    # ---------------------------------------------
    try:
        geoprocess = payload["geoprocess"]
        GeoCfg = namedtuple("GeoCfg", payload["geoprocess_config"])(
            **payload["geoprocess_config"]
        )

        # dst = TemporaryDirectory()
        product_slug = lookup_product_slug_by_acquirablefile_id(af["id"])
        if product_slug is not None:
            dst_path = f"{products_dir}/{product_slug}"
            if not os.path.isdir(dst_path):
                os.makedirs(name=dst_path, exist_ok=False)

            handler.handle_message(geoprocess, GeoCfg, dst_path)
        else:
            print(f"Unable to find acquirablefile_id: {af['id']}")
    except Exception as ex:
        print(traceback.format_exc())
    # finally:
    #     if os.path.exists(dst.name):
    #         shutil.rmtree(dst.name, ignore_errors=True)
    #     dst = None

# ------------------------------------------------------------------
# Loop through products on disk, find matching S3/Minio product file,
# compare using gdalcompare
# ------------------------------------------------------------------
files_checked = []
total_diffs = 0
total_cog_validation_errors = 0

for subdir, dirs, files in os.walk(products_dir):
    files = [fi for fi in files if fi.endswith(".tif")]
    for file in files:

        print(file)

        new_file = os.path.join(subdir, file)
        key = new_file.replace("/tmp/", "")

        # Download the "golden" aka known good file so
        # gdalcompare can do a binary comparison (not possible over vsi driver)
        golden_file = new_file.replace("/products/", "/products_golden/")
        golden_file_dir = os.path.dirname(golden_file)
        if not os.path.isdir(golden_file_dir):
            os.makedirs(name=golden_file_dir, exist_ok=False)
        golden_file = s3_download_file(BUCKET, key, None, golden_file_dir)

        # # sys.stdout = open(os.devnull, "w")
        # # sys.stderr = open(os.devnull, "w")

        print(f"Checking {new_file}")

        diff = gdalcompare.find_diff(
            golden_file=golden_file, new_file=new_file, check_sds=True
        )
        total_diffs = total_diffs + diff

        # sys.stdout = sys.__stdout__
        # sys.stderr = sys.__stderr__

        print("Validating new COG...")
        cog_validation_check = validate_cloud_optimized_geotiff.validate(golden_file)
        if len(cog_validation_check[0]) > 0:
            print(f"COG has ERRORS -> {cog_validation_check[0]}")
            for e in cog_validation_check[0]:
                cog_validation_errors = cog_validation_errors + 1
        else:
            print("No errors")

        files_checked.append(file)

        print("-" * 64)


print("*" * 64)
print(f"Files checked: {len(files_checked)}")
print(f"Total Differences: {total_diffs}")
print(f"COG Validation Errors: {total_cog_validation_errors}")
print("*" * 64)
