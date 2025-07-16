import json
import os

import jsonschema
import referencing
import requests
from referencing.jsonschema import DRAFT7

API_ROOT_PATH = os.environ.get("API_ROOT_PATH", "")
API_ROOT_PATH = API_ROOT_PATH if API_ROOT_PATH.endswith("/") else f"{API_ROOT_PATH}/"

format_checking = jsonschema.FormatChecker(formats=["date", "date-time"])

schemas = {}
for schema_def in (
    "dataset_preview",
    "dataset",
    "datasets",
):
    with open(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "..",
            "schemas",
            f"{schema_def}.json",
        ),
        "r",
    ) as f:
        schemas[f"/schemas/{schema_def}"] = json.load(f)


def retrieve_via_requests(uri):
    response = requests.get(uri)
    return referencing.Resource.from_contents(response.json())


registry = referencing.Registry(retrieve=retrieve_via_requests).with_resources(
    [
        (uri, referencing.Resource.from_contents(schema, default_specification=DRAFT7))
        for uri, schema in schemas.items()
    ]
)

resolver = registry.resolver()
resolver.lookup(
    "https://raw.githubusercontent.com/radiantearth/stac-spec/v1.1.0/collection-spec/json-schema/collection.json"
)


collection_set_validator = jsonschema.validators.validator_for(
    schemas["/schemas/datasets"]
)(
    schema=schemas["/schemas/datasets"],
    registry=registry,
    format_checker=format_checking,
)

collection_validator = jsonschema.validators.validator_for(schemas["/schemas/dataset"])(
    schema=schemas["/schemas/dataset"],
    registry=registry,
    format_checker=format_checking,
)


def test_stac_collection_set_conformance() -> None:
    r = requests.get(f"{API_ROOT_PATH}collections")

    assert r.status_code == 200
    collection_set_validator.validate(r.json())


def test_stac_collection_conformance() -> None:
    r = requests.get(f"{API_ROOT_PATH}collections")
    collections = r.json()["collections"]
    for collection in collections:
        collections_url = [
            link for link in collection["links"] if link["rel"] == "self"
        ][0]["href"]
        r = requests.get(collections_url)

        assert r.status_code == 200
        collection_validator.validate(r.json())
