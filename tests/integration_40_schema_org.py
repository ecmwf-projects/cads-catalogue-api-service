import os

import requests

API_ROOT_PATH = os.environ.get("API_ROOT_PATH", "")
API_ROOT_PATH = API_ROOT_PATH if API_ROOT_PATH.endswith("/") else f"{API_ROOT_PATH}/"


def test_schema_org() -> None:
    r = requests.get(f"{API_ROOT_PATH}collections/dummy-dataset/schema.org")
    assert r.status_code == 200
