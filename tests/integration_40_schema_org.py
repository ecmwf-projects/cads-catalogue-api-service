import json
import os

import jsonschema
import referencing
import requests
from referencing.jsonschema import DRAFT7

API_ROOT_PATH = os.environ.get("API_ROOT_PATH", "")
API_ROOT_PATH = API_ROOT_PATH if API_ROOT_PATH.endswith("/") else f"{API_ROOT_PATH}/"

format_checking = jsonschema.FormatChecker(formats=["date", "date-time"])

ref_mapping = {}

with open(
    os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "..",
        "schemas",
        "schema_org.json",
    ),
    "r",
) as f:
    ref_mapping["/schemas/schema_org"] = json.load(f)

registry = referencing.Registry().with_resources(
    [
        (uri, referencing.Resource.from_contents(schema, default_specification=DRAFT7))
        for uri, schema in ref_mapping.items()
    ]
)

SchemaValidator = jsonschema.validators.validator_for(
    ref_mapping["/schemas/schema_org"]
)

schema_org_validator = jsonschema.validators.validator_for(
    ref_mapping["/schemas/schema_org"]
)(
    schema=ref_mapping["/schemas/schema_org"],
    registry=registry,
    format_checker=format_checking,
)


SchemaValidator(
    schema=ref_mapping["/schemas/schema_org"],
    resolver=jsonschema.RefResolver("", {}, store=ref_mapping),
)


def test_schema_org() -> None:
    r = requests.get(
        f"{API_ROOT_PATH}collections/reanalysis-era5-single-levels/schema.org"
    )
    assert r.status_code == 200

    results = r.json()

    assert (
        schema_org_validator.validate(results, ref_mapping["/schemas/schema_org"])
        is None
    )
