import json
import os

import jsonschema
import requests

API_ROOT_PATH = os.environ.get("API_ROOT_PATH", "")
API_ROOT_PATH = API_ROOT_PATH if API_ROOT_PATH.endswith("/") else f"{API_ROOT_PATH}/"

with open(
    os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "schemas/datasets.json"
    ),
    "r",
) as f:
    collection_set_schema = json.load(f)

with open(
    os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "schemas/dataset.json"
    ),
    "r",
) as f:
    collection_schema = json.load(f)

ref_mapping = {
    "/schemas/datasets": collection_set_schema,
    "/schemas/dataset": collection_schema,
}

CollectionSetValidator = jsonschema.validators.validator_for(collection_set_schema)
CollectionValidator = jsonschema.validators.validator_for(collection_schema)

collection_set_validator = CollectionSetValidator(
    schema=collection_set_schema,
    resolver=jsonschema.RefResolver("", {}, store=ref_mapping),
)
collection_validator = CollectionValidator(
    schema=collection_schema, resolver=jsonschema.RefResolver("", {}, store=ref_mapping)
)


def test_stac_collection_set_conformance() -> None:
    r = requests.get(f"{API_ROOT_PATH}collections")

    assert r.status_code == 200
    assert collection_set_validator.validate(r.json(), collection_set_schema) is None


def test_stac_collection_conformance() -> None:
    r = requests.get(f"{API_ROOT_PATH}collections")
    collections = r.json()["collections"]
    for collection in collections:
        collections_url = [
            link for link in collection["links"] if link["rel"] == "self"
        ][0]["href"]
        r = requests.get(collections_url)

        assert r.status_code == 200
        assert collection_validator.validate(r.json(), collection_schema) is None
