import os

import requests

API_ROOT_PATH = os.environ.get("API_ROOT_PATH", "")
API_ROOT_PATH = API_ROOT_PATH if API_ROOT_PATH.endswith("/") else f"{API_ROOT_PATH}/"


def test_licences_vocabulary() -> None:
    # TODO: replace with a JSON schema, and iterate on all entries
    r = requests.get(f"{API_ROOT_PATH}vocabularies/licences")

    assert r.status_code == 200

    results = r.json()
    licences = results.get("licences")

    assert type(licences) == list
    assert type(licences[0]) == dict
    assert type(licences[0].get("id")) == str
    assert type(licences[0].get("label")) == str
    assert type(licences[0].get("revision")) == int
