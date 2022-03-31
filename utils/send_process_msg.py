"""Local development testing products
    Sending a message to the SQS queue for the geoprocessor
    Products should be under the following directory structure:

        <repo dir>/data/cumulus/acquirables/<acquirable slug>/<product>

    Raises
    ------
    Exception
        None.  Never errors. :)

    Usage
    -----
    Example: Send message for all files
        >>> python send_process_msg.py

    Example: Send message for files using filter that contain 'Pass1'
        >>> python send_process_msg.py -f .*Pass1.*

    Adding switch '-n' will 'dry-run' each execution printing the message(s)
"""

import os
import re
import json
import argparse
from typing import NamedTuple
import boto3
from minio import Minio


class GeoProcess(NamedTuple):
    geoprocess: str
    geoprocess_config: dict


class GeoProcessConfig(NamedTuple):
    bucket: str
    key: str
    acquirablefile_id: str
    acquirable_id: str
    acquirable_slug: str


class PathExpandAction(argparse.Action):
    """Argument parser action used to "expanduser" and "expandvars"

    Inheritance of argparse.Action using super() method to extend the base class
    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise Exception('"nargs" not allowed')
        super(PathExpandAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if values == "-":
            setattr(namespace, self.dest, None)
        else:
            values = os.path.realpath(os.path.expandvars(os.path.expanduser(values)))
            setattr(namespace, self.dest, values)


parser = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument(
    "-b",
    "--bucket",
    action="append",
    default=["castle-data-develop"],
    help='AWS (minio) bucket name; default="%(default)s"',
)
parser.add_argument("-f", "--filter", help="Regex filter string for filenames")
parser.add_argument(
    "-n", "--dry-run", action="store_true", help="Dry-run to see the message(s)"
)
args = parser.parse_args()

# Make sure the list of buckets is unique
bucket_set = set(args.bucket)
args.bucket = list(bucket_set)

mClient = Minio(
    "localhost:9000",
    access_key="AKIAIOSFODNN7EXAMPLE",
    secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    secure=False,
)

bClient = boto3.resource(
    "sqs",
    endpoint_url="http://localhost:9324",
    region_name="elasticmq",
    aws_secret_access_key="x",
    aws_access_key_id="x",
    use_ssl=False,
)
queue = bClient.get_queue_by_name(QueueName="cumulus-geoprocess")

filter = re.compile(args.filter) if args.filter else re.compile(r".*")
exclude = re.compile(r"^.*/\..*$")

bucket_count = 0
object_count = 0

for bucket in args.bucket:
    if mClient.bucket_exists(bucket):
        bucket_count += 1
        objects = mClient.list_objects(bucket, recursive=True)
        for object in objects:
            object_name = object.object_name
            if m := exclude.match(object_name):
                print(f'Excluded match "{m[0]}"')
            elif m := filter.match(object_name):
                object_count += 1
                cog_config = GeoProcessConfig(bucket, object_name)
                msg_cog = GeoProcess("incoming-file-to-cogs", cog_config._asdict())
                body = json.dumps(msg_cog._asdict(), indent=4)
                if args.dry_run:
                    print(body)
                else:
                    response = queue.send_message(MessageBody=body)

print(f"{bucket_count=}", f"{object_count=}")
