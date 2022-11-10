import json
import os

import jsonschema
import requests

API_ROOT_PATH = os.environ.get("API_ROOT_PATH", "")
API_ROOT_PATH = API_ROOT_PATH if API_ROOT_PATH.endswith("/") else f"{API_ROOT_PATH}/"

format_checking = jsonschema.FormatChecker(formats=["date", "date-time"])

ref_mapping = {}

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
        ref_mapping[f"/schemas/{schema_def}"] = json.load(f)


CollectionSetValidator = jsonschema.validators.validator_for(
    ref_mapping["/schemas/datasets"]
)
CollectionValidator = jsonschema.validators.validator_for(
    ref_mapping["/schemas/dataset"]
)

collection_set_validator = CollectionSetValidator(
    schema=ref_mapping["/schemas/datasets"],
    resolver=jsonschema.RefResolver("", {}, store=ref_mapping),
    format_checker=format_checking,
)
collection_validator = CollectionValidator(
    schema=ref_mapping["/schemas/dataset_preview"],
    resolver=jsonschema.RefResolver("", {}, store=ref_mapping),
)


def test_stac_collection_set_conformance() -> None:
    r = requests.get(f"{API_ROOT_PATH}collections")

    assert r.status_code == 200
    assert (
        collection_set_validator.validate(r.json(), ref_mapping["/schemas/datasets"])
        is None
    )


def test_stac_collection_conformance() -> None:
    r = requests.get(f"{API_ROOT_PATH}collections")
    collections = r.json()["collections"]
    for collection in collections:
        collections_url = [
            link for link in collection["links"] if link["rel"] == "self"
        ][0]["href"]
        r = requests.get(collections_url)

        assert r.status_code == 200
        assert (
            collection_validator.validate(r.json(), ref_mapping["/schemas/dataset"])
            is None
        )
