import json
import os

import jsonschema
import requests

API_ROOT_PATH = os.environ.get("API_ROOT_PATH", "")
API_ROOT_PATH = API_ROOT_PATH if API_ROOT_PATH.endswith("/") else f"{API_ROOT_PATH}/"


format_checking = jsonschema.FormatChecker(formats=["date", "date-time"])

ref_mapping = {}


for schema_def in ("messages", "changelog"):
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

MessageValidator = jsonschema.validators.validator_for(ref_mapping["/schemas/messages"])
ChangelogValidator = jsonschema.validators.validator_for(
    ref_mapping["/schemas/changelog"]
)

message_validator = MessageValidator(
    schema=ref_mapping["/schemas/messages"],
    resolver=jsonschema.RefResolver("", {}, store=ref_mapping),
)
changelog_validator = ChangelogValidator(
    schema=ref_mapping["/schemas/changelog"],
    resolver=jsonschema.RefResolver("", {}, store=ref_mapping),
)


def test_messages() -> None:
    r = requests.get(f"{API_ROOT_PATH}messages")

    assert r.status_code == 200

    results = r.json()
    messages = results.get("messages")

    assert type(messages) == list
    assert message_validator.validate(results, ref_mapping["/schemas/messages"])


def test_changelog_messages() -> None:
    r = requests.get(f"{API_ROOT_PATH}messages/changelog")

    assert r.status_code == 200

    results = r.json()
    changelog_list = results.get("changelog")

    assert type(changelog_list) == list
    assert changelog_validator.validate(results, ref_mapping["/schemas/changelog"])
