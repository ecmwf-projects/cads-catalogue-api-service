import os

import requests

API_ROOT_PATH = os.environ.get("API_ROOT_PATH", "")
API_ROOT_PATH = API_ROOT_PATH if API_ROOT_PATH.endswith("/") else f"{API_ROOT_PATH}/"


def test_licences_vocabulary() -> None:
    # TODO: replace with a JSON schema
    r = requests.get(f"{API_ROOT_PATH}vocabularies/licences")

    assert r.status_code == 200

    results = r.json()
    licences = results.get("licences")

    assert type(licences) == list
    for licence in licences:
        assert type(licence) == dict
        assert type(licence.get("id")) == str
        assert type(licence.get("label")) == str
        assert type(licence.get("revision")) == int
