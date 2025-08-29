import logging
import os

import pytest
import requests

API_ROOT_PATH = os.environ.get("API_ROOT_PATH", "")
API_ROOT_PATH = API_ROOT_PATH if API_ROOT_PATH.endswith("/") else f"{API_ROOT_PATH}/"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@pytest.fixture
def collection_by_id(request):
    """Fixture che restituisce una collezione specifica per ID."""
    collection_id = request.param
    r = requests.get(f"{API_ROOT_PATH}collections/{collection_id}")
    assert r.status_code == 200
    return r.json()


def get_collection_ids():
    r = requests.get(f"{API_ROOT_PATH}collections")
    if r.status_code != 200:
        raise Exception("Failed to retrieve collections")
    collections = r.json()["collections"]
    return [collection["id"] for collection in collections]


@pytest.mark.parametrize(
    "collection_by_id",
    get_collection_ids(),
    indirect=True,
    ids=lambda x: f"collection_{x}",
)
def test_collections_links(collection_by_id) -> None:
    for link in collection_by_id["links"]:
        if link["rel"] not in [
            "self",
            "parent",
            "root",
        ]:
            logger.info(f"Checking {collection_by_id['title']}, rel {link['rel']}")
            link_req = requests.get(link["href"])
            assert link_req.status_code == 200
