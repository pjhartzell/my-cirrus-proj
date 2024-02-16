#!/usr/bin/env python
import json
from pathlib import Path
import sys
import os
from typing import Any, Dict

import boto3
import pystac
import pystac_client
from cirrus.lib2.process_payload import ProcessPayload
from cirrus.lib2.logging import get_task_logger

LAMBDA_TYPE = "feeder"
EARTHSEARCH_ENDPOINT = "https://earth-search.aws.element84.com/v1"
DATA_BUCKET = "cirrus-dev-data-pknrs01xxceg"
QUEUE_URL = os.getenv("CIRRUS_PROCESS_QUEUE_URL")
SQS_RESOURCE = boto3.resource("sqs")


def validate_input_payload(feeder_input: Dict[str, Any]) -> bool:
    if feeder_input.get("assets") is None:
        raise ValueError("No 'assets' key specified in feeder input")
    if feeder_input.get("crs") is None:
        raise ValueError("No 'crs' key specified in feeder input")


def get_sentinel_2_item() -> pystac.Item:
    catalog = pystac_client.Client.open(EARTHSEARCH_ENDPOINT)
    search = catalog.search(collections=["sentinel-2-c1-l2a"], max_items=1)
    item = next(search.items())
    if item is None:
        raise ValueError("No sentinel-2-c1-l2a Items found in EarthSearch")
    return item


def create_process_block(feeder_input: Dict[str, Any]) -> Dict[str, Any]:
    tasks = {
        "download": {
            "assets": feeder_input.get("assets"),
        },
        "reproject": {
            "crs": feeder_input.get("crs"),
            "assets": feeder_input.get("assets"),
        },
    }

    upload_options = {
        "path_template": (
            f"s3://{DATA_BUCKET}/${{collection}}/${{year}}/${{month}}/${{id}}"
        ),
        "collections": {
            "sentinel-2-c1-l2a": "S2.*",
            "reprojected-sentinel-2-c1-l2a": "REP_S2.*",
        },
        "s3_urls": True,
    }

    process_block = {
        "description": "Download and reproject Sentinel-2 data",
        "workflow": "reproject-sentinel-2",
        "upload_options": upload_options,
        "tasks": tasks,
    }

    return process_block


def create_output_payload(event: Dict[str, Any]) -> Dict[str, Any]:
    item = get_sentinel_2_item()
    process_block = create_process_block(event)

    payload_dict = pystac.ItemCollection(
        items=[item],
        extra_fields={"process": process_block},
    ).to_dict()

    # NOTE: the .get_payload() method will upload the payload to s3 if size>30KB
    return ProcessPayload(payload_dict, set_id_if_missing=True).get_payload()


def lambda_handler(event, context={}):
    logger = get_task_logger(
        f"{LAMBDA_TYPE}.earthsearch-sentinel-2",
        payload={
            "id": "Not a ProcessPayload",
        },
    )

    validate_input_payload(event)

    payload = create_output_payload(event)

    if not event.get("dry_run", True):
        queue = SQS_RESOURCE.Queue(QUEUE_URL)
        queue.send_message(MessageBody=json.dumps(payload))
        logger.info(f"Sent payload with id={payload['id']} to {QUEUE_URL}")

    return payload


if __name__ == "__main__":
    """Pass the input payload file as the first argument to the script. The output
    payload will be written to a file with the same name as the input file, but with the
    _out.json suffix.

    Example input payload:
    {
        "assets": ["red", "green", "blue"],  # assets to reproject
        "crs": "EPSG:4326",  # target reprojection CRS
        "dry_run": false,  # whether to send the payload to the queue
    }
    """
    input_payload_file = sys.argv[1]
    with open(input_payload_file, "r") as f:
        input_payload = json.load(f)
    output_payload = lambda_handler(input_payload)
    with open(Path(input_payload_file).with_suffix(".out.json"), "w") as f:
        f.write(json.dumps(output_payload, indent=4))
