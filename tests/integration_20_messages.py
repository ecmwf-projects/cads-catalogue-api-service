import os

import requests

API_ROOT_PATH = os.environ.get("API_ROOT_PATH", "")
API_ROOT_PATH = API_ROOT_PATH if API_ROOT_PATH.endswith("/") else f"{API_ROOT_PATH}/"


def test_messages() -> None:
    # TODO: replace with a JSON schema
    r = requests.get(f"{API_ROOT_PATH}messages")

    assert r.status_code == 200

    results = r.json()
    messages = results.get("messages")

    assert type(messages) == list
    for message in messages:
        assert type(message) == dict
        assert type(message.get("id")) == str
        assert type(message.get("date")) == str
        assert type(message.get("summary")) == str
        assert type(message.get("url")) == str
        assert type(message.get("severity")) == str
        assert type(message.get("links")) == list


def test_changelogs_messages() -> None:
    # TODO: replace with a JSON schema
    r = requests.get(f"{API_ROOT_PATH}messages/changelogs")

    assert r.status_code == 200

    results = r.json()
    changelogs = results.get("changelogs")

    assert type(changelogs) == list
    for changelog in changelogs:
        assert type(changelog) == dict
        assert type(changelog.get("id")) == str
        assert type(changelog.get("date")) == str
        assert type(changelog.get("summary")) == str
        assert type(changelog.get("url")) == str
        assert type(changelog.get("severity")) == str
        assert type(changelog.get("archived")) == bool
        assert type(changelog.get("links")) == list
