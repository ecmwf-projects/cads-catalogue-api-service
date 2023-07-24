import os

import requests

API_ROOT_PATH = os.environ.get("API_ROOT_PATH", "")
API_ROOT_PATH = API_ROOT_PATH if API_ROOT_PATH.endswith("/") else f"{API_ROOT_PATH}/"


def test_collections_links() -> None:
    r = requests.get(f"{API_ROOT_PATH}datasets")

    assert r.status_code == 200

    results = r.json()
    collections = results["collections"]
    for collection in collections:
        for link in collection["links"]:
            if link["rel"] not in ["self", "parent"]:
                link_req = requests.head(link["href"])
                if link_req.status_code != 200:
                    assert False
