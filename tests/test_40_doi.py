# Copyright 2024, European Union.
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

from typing import Any

import fastapi
import fastapi.testclient
import sqlalchemy as sa
import stac_fastapi.types
import stac_fastapi.types.core

from cads_catalogue_api_service.main import app

client = fastapi.testclient.TestClient(app)


def static_collection(
    session: Any,
    request: Any,
    collection_id: str | None = None,
) -> stac_fastapi.types.stac.Collection:
    return {
        "type": "Collection",
        "id": "era5-something",
        "stac_version": "1.0.0",
        "title": "Era5 name",
        "description": "This dataset provides a modelled time series of gridded river discharge.",
        "keywords": [
            "Temporal coverage: Past",
        ],
        "links": [
            {
                "rel": "self",
                "type": "application/json",
                "href": "http://localhost:8080/api/catalogue/v1/collections/era5-something",
            },
        ],
    }


def error_static_collection_query(error: Exception):
    def query_collection(
        session: sa.orm.Session,
        doi: str,
        request: fastapi.Request,
    ) -> stac_fastapi.types.stac.Collection:
        raise error

    return query_collection


def test_doi_error(monkeypatch) -> None:
    monkeypatch.setattr(
        "cads_catalogue_api_service.doi.query_collection",
        error_static_collection_query(sa.orm.exc.NoResultFound("foo bar not found")),
    )

    response = client.get(
        "/doi/11111/doi",
    )

    assert response.status_code == 404
    assert response.json()["title"] == "Dataset not found"

    monkeypatch.setattr(
        "cads_catalogue_api_service.doi.query_collection",
        error_static_collection_query(
            sa.orm.exc.MultipleResultsFound("multiple foo ba")
        ),
    )

    response = client.get(
        "/doi/11111/doi",
    )

    assert response.status_code == 500
    assert response.json()["title"] == "Error while searching for this DOI"


def test_doi_redirect(monkeypatch) -> None:
    monkeypatch.setattr(
        "cads_catalogue_api_service.doi.query_collection",
        static_collection,
    )

    response = client.get("/doi/11111/22222", allow_redirects=False)

    assert response.status_code == 301
    assert response.headers["location"] == "/datasets/era5-something"
