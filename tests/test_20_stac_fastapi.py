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
import stac_fastapi.types

import cads_catalogue_api_service.client
import cads_catalogue_api_service.main

client = fastapi.testclient.TestClient(cads_catalogue_api_service.main.app)


class Extension:
    def __init__(self) -> None:
        self.conformance_classes = ["foo bar", "baz"]


def test_conformance_classes() -> None:
    client = cads_catalogue_api_service.client.CatalogueClient()
    client.extensions = [Extension()]

    conformance_classes = client.conformance_classes()

    assert "foo bar" in conformance_classes
    assert "baz" in conformance_classes
    assert (
        stac_fastapi.types.conformance.STACConformanceClasses.CORE
        in conformance_classes
    )


def test_openapi() -> None:
    result = cads_catalogue_api_service.main.app.openapi()

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

    assets = cads_catalogue_api_service.client.generate_assets(model, "http://foo.org")

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
    assert response.json()["detail"] == "STAC search is not implemented"

    # TODO testing client.post("/search") which is not working due to stac_fastapi internal implementation details.  # noqa: E501
