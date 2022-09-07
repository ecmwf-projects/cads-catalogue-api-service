import json
import os

import jsonschema
import requests

API_ROOT_PATH = os.environ.get("API_ROOT_PATH", "")
API_ROOT_PATH = API_ROOT_PATH if API_ROOT_PATH.endswith("/") else f"{API_ROOT_PATH}/"

SCHEMA_ROOT_PATH = os.environ.get("SCHEMA_ROOT_PATH", "")


with open("schemas/datasets.json", "r") as f:
    schema = json.load(f)


def test_stac_collection_set_conformance() -> None:
    r = requests.get(f"{API_ROOT_PATH}collections")

    assert r.status_code == 200
    assert jsonschema.validate(r.json(), schema) is None
