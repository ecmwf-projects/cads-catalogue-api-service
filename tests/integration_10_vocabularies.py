import json
import os

import jsonschema
import requests

API_ROOT_PATH = os.environ.get("API_ROOT_PATH", "")
API_ROOT_PATH = API_ROOT_PATH if API_ROOT_PATH.endswith("/") else f"{API_ROOT_PATH}/"


ref_mapping = {}

for schema_def in ("keywords", "licences"):
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

KeywordsValidator = jsonschema.validators.validator_for(
    ref_mapping["/schemas/keywords"]
)
LicencesValidator = jsonschema.validators.validator_for(
    ref_mapping["/schemas/licences"]
)

keyword_validator = KeywordsValidator(
    schema=ref_mapping["/schemas/keywords"],
    resolver=jsonschema.RefResolver("", {}, store=ref_mapping),
)
licence_validator = LicencesValidator(
    schema=ref_mapping["/schemas/licences"],
    resolver=jsonschema.RefResolver("", {}, store=ref_mapping),
)


def test_licences_vocabulary() -> None:
    r = requests.get(f"{API_ROOT_PATH}vocabularies/licences")

    assert r.status_code == 200

    results = r.json()
    licences = results.get("licences")

    assert type(licences) == list
    assert licence_validator.validate(results, ref_mapping["/schemas/licences"])


def test_keywords_vocabulary() -> None:
    r = requests.get(f"{API_ROOT_PATH}vocabularies/keywords")

    assert r.status_code == 200

    results = r.json()
    licences = results.get("keywords")

    assert type(licences) == list
    assert keyword_validator.validate(results, ref_mapping["/schemas/keywords"])
