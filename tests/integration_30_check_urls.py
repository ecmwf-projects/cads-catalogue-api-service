import logging
import os

import requests

API_ROOT_PATH = os.environ.get("API_ROOT_PATH", "")
API_ROOT_PATH = API_ROOT_PATH if API_ROOT_PATH.endswith("/") else f"{API_ROOT_PATH}/"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def test_collections_links() -> None:
    r = requests.get(f"{API_ROOT_PATH}collections")

    assert r.status_code == 200

    results = r.json()
    collections = results["collections"]
    for collection in collections:
        for link in collection["links"]:
            if link["rel"] not in [
                "self",
                "parent",
                "root",
            ]:
                logger.info(f"Checking link with rel {link['rel']}")
                link_req = requests.head(link["href"])
                assert link_req.status_code == 200
