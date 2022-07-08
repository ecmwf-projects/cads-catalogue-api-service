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

import cads_catalogue.database
import fastapi.testclient
import pytest
import sqlalchemy.orm
import stac_fastapi.types
from testing import generate_expected, get_record

import cads_catalogue_api_service.main
from cads_catalogue_api_service import main

client = fastapi.testclient.TestClient(main.app)


class Request:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url


class ResultSet:
    def __init__(self, items: list[str] = []) -> None:
        self._results = [get_record(item) for item in items]

    def all(self) -> list[cads_catalogue.database.Resource]:
        return self._results

    def filter(self, *args, **kwargs):  # type: ignore
        return ResultSet(["era5-something", "soil-mosture"])

    def one(self):  # type: ignore
        try:
            return self._results[0]
        except IndexError:
            raise (sqlalchemy.orm.exc.NoResultFound)


class DBSession:
    def query(self, *args, **kwargs):  # type: ignore
        return ResultSet(["era5-something", "soil-mosture"])

    def filter(self, condition, *args, **kwargs):  # type: ignore
        if condition:
            return ResultSet(["era5-something", "soil-mosture"])
        return ResultSet()


class Record:

    __name__ = "a-table"

    @property
    def resource_uid(self):  # type: ignore
        return "era5-something"


class ContextSession:
    def __enter__(self):  # type: ignore
        return DBSession()

    def __exit__(self, *args):  # type: ignore
        pass


class Reader:
    def context_session(self):  # type: ignore
        return ContextSession()


class Session(sqlalchemy.orm.Session):
    def query(self, *args, **kwargs):  # type: ignore
        return DBSession()


class Extension:
    def __init__(self) -> None:
        self.conformance_classes = ["foo bar", "baz"]


def test_get_all_collections() -> None:
    client = cads_catalogue_api_service.main.CatalogueClient()
    client.reader = Reader()

    results = client.all_collections(Request("http://foo.org"))

    assert len(results["collections"]) == 2
    assert results["collections"][0] == generate_expected(preview=True)


def test_lookup_id() -> None:
    lookup_id = cads_catalogue_api_service.main.lookup_id
    session = Session()
    expected = generate_expected()

    result = lookup_id("era5-something", Record(), session)

    assert result.resource_uid == expected["id"]
    assert result.description == expected["tmp:description"]

    with pytest.raises(stac_fastapi.types.errors.NotFoundError):
        lookup_id("will-not-find-this", Record(), session)


def test_get_collection() -> None:
    client = cads_catalogue_api_service.main.CatalogueClient()
    client.collection_table = Record()
    client.reader = Reader()
    expected = generate_expected()

    result = client.get_collection("era5-something", Request("http://foo.org"))

    assert result["id"] == expected["id"]
    assert result["description"] == expected["description"]


def test_conformance_classes() -> None:
    client = cads_catalogue_api_service.main.CatalogueClient()
    client.extensions = [Extension()]

    conformance_classes = client.conformance_classes()

    assert "foo bar" in conformance_classes
    assert "baz" in conformance_classes
    assert (
        stac_fastapi.types.conformance.STACConformanceClasses.CORE
        in conformance_classes
    )


def test_openapi() -> None:
    result = main.app.openapi()

    assert result["openapi"] >= "3.0.0"
    assert "/collections" in result["paths"].keys()
    assert "/collections/{collection_id}" in result["paths"].keys()
    with pytest.raises(KeyError):
        result["paths"]["/search"]
    with pytest.raises(KeyError):
        result["paths"]["/collections/{id}/items"]
    with pytest.raises(KeyError):
        result["paths"]["/collections/{collection_id}/items/{item_id}"]


def test_generate_assets() -> None:
    model = cads_catalogue.database.Resource(
        resource_uid="era5-something", previewimage="foo/bar/baz/preview.webp"
    )

    assets = cads_catalogue_api_service.main.generate_assets(model, "http://foo.org")

    assert assets == {
        "thumbnail": {
            "href": "http://foo.org/foo/bar/baz/preview.webp",
            "roles": ["thumbnail"],
            "type": "image/jpg",
        },
    }


def test_error_handler() -> None:
    """Test that an HTTP 501 is returned in case of not implemented (but still valid) STAC routes."""
    response = client.get("/collections/a-dataset/items")

    assert response.status_code == 501

    response = client.get("/collections/a-dataset/items/ad-item")

    assert response.status_code == 501


def test_search_not_implemented() -> None:
    response = client.get("/search")

    assert response.status_code == 501
    assert response.json()["message"] == "STAC search is not implemented"

    # TODO testing client.post("/search") which is not working due to stac_fastapi internal details.
