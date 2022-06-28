# Copyright 2022, European Union.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

import fastapi.testclient
import pytest
from testing import get_record

import cads_catalogue_api_service.main
from cads_catalogue_api_service import main

client = fastapi.testclient.TestClient(main.app)


expected = {
    "type": "Collection",
    "id": "era5-something",
    "stac_version": "1.0.0",
    "title": "ERA5",
    "description": {"description": "aaaa"},
    "keywords": ["label 1", "label 2"],
    "providers": ["provider 1", "provider 2"],
    "summaries": None,
    "extent": [[-180, 180], [-90, 90]],
    "links": [
        {
            "rel": "self",
            "type": "application/json",
            "href": "http://foo.org/collections/era5-something",
        },
        {
            "rel": "parent",
            "type": "application/json",
            "href": "http://foo.org",
        },
        {
            "rel": "root",
            "type": "application/json",
            "href": "http://foo.org",
        },
        {"rel": "foo", "href": "http://foo.com"},
    ],
}


class Request:
    def __init__(self, base_url):
        self.base_url = base_url


class ResultSet:
    def __init__(self):
        self._results = [get_record("era5-something"), get_record("soil-mosture")]

    def all(self):
        return self._results

    def first(self):
        return self._results[0]


class DBSession:
    def query(*args, **kwargs):
        return ResultSet()

    def filter(*args, **kwargs):
        return ResultSet()


class Table:
    @property
    def resource_id(self):
        return "foo-table"


class ContextSession:
    def __enter__(self):
        return DBSession()

    def __exit__(self, *args):
        pass


class Context:
    def context_session(self):
        return ContextSession()


class Session:
    def __init__(self):
        self.reader = Context()

    def query(*args, **kwargs):
        return DBSession()


def test_error_handler() -> None:
    """Test that an HTTP 501 is returned in case of not implemented (but still valid) STAC routes."""
    response = client.get("/collections/a-dataset/items")

    assert response.status_code == 501

    response = client.get("/collections/a-dataset/items/ad-item")

    assert response.status_code == 501


def test_get_all_collections():
    client = cads_catalogue_api_service.main.CatalogueClient()
    client.session = Session()

    results = client.all_collections(Request("http://foo.org"))

    assert len(results["collections"]) == 2
    assert json.dumps(results["collections"][0]) == json.dumps(expected)


def test_lookup_id():
    lookup_id = cads_catalogue_api_service.main.CatalogueClient._lookup_id
    session = Session()

    result = lookup_id("era5-something", Table(), session)

    assert result.resource_id == expected["id"]
    assert result.description == expected["description"]


def test_openapi():
    result = main.app.openapi()

    assert result["openapi"] >= "3.0.0"
    assert "/collections" in result["paths"].keys()
    assert "/collections/{collection_id}" in result["paths"].keys()
    with pytest.raises(KeyError):
        result["paths"]["/search"]
        result["paths"]["/collections/{id}/items"]
        result["paths"]["/collections/{collection_id}/items/{item_id}"]
