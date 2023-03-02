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
        assert type(message.get("message_id")) == str
        assert type(message.get("date")) == str
        assert type(message.get("summary")) == str
        assert type(message.get("url")) == str
        assert type(message.get("severity")) == str
        assert type(message.get("content")) == str
        assert type(message.get("live")) == bool
        assert type(message.get("status")) == str


def test_changelog_messages() -> None:
    # TODO: replace with a JSON schema
    r = requests.get(f"{API_ROOT_PATH}messages/changelog")

    assert r.status_code == 200

    results = r.json()
    changelog_list = results.get("changelog")

    assert type(changelog_list) == list
    for changelog in changelog_list:
        assert type(changelog) == dict
        assert type(changelog.get("message_id")) == str
        assert type(changelog.get("date")) == str
        assert type(changelog.get("summary")) == str
        assert type(changelog.get("url")) == str
        assert type(changelog.get("severity")) == str
        assert type(changelog.get("content")) == str
        assert type(changelog.get("live")) == bool
        assert type(changelog.get("status")) == str
