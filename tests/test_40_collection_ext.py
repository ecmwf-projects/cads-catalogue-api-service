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

from cads_catalogue_api_service.main import app

client = fastapi.testclient.TestClient(app)


def _static_query_collection(
    session: Any,
    collection_id: str,
    request: fastapi.Request,
):
    return {
        "type": "Collection",
        "id": "era5-something",
        "stac_version": "1.1.0",
        "title": "Era5 name",
        "description": "This dataset provides a modelled time series of gridded river discharge.",
        "keywords": [
            "Temporal coverage: Past",
        ],
        "license": "other",
        "links": [
            {
                "rel": "self",
                "type": "application/json",
                "href": "http://localhost:8080/api/catalogue/v1/collections/era5-something",
            },
            {
                "rel": "parent",
                "type": "application/json",
                "href": "http://localhost:8080/api/catalogue/v1/",
            },
            {
                "rel": "root",
                "type": "application/json",
                "href": "http://localhost:8080/api/catalogue/v1/",
            },
            {
                "rel": "form",
                "type": "application/json",
                "href": "https://somewhere.or/s3/form.json",
            },
            {
                "rel": "constraints",
                "type": "application/json",
                "href": "https://somewhere.or/s3/constraints.json",
            },
        ],
    }


def _static_query_collection_nolinks(
    session: Any,
    collection_id: str,
    request: fastapi.Request,
):
    return {
        "type": "Collection",
        "id": "era5-something",
        "stac_version": "1.1.0",
        "title": "Era5 name",
        "description": "This dataset provides a modelled time series of gridded river discharge.",
        "keywords": [
            "Temporal coverage: Past",
        ],
        "license": "other",
        "links": [
            {
                "rel": "self",
                "type": "application/json",
                "href": "http://localhost:8080/api/catalogue/v1/collections/era5-something",
            },
            {
                "rel": "parent",
                "type": "application/json",
                "href": "http://localhost:8080/api/catalogue/v1/",
            },
            {
                "rel": "root",
                "type": "application/json",
                "href": "http://localhost:8080/api/catalogue/v1/",
            },
        ],
    }


def test_ext_form(monkeypatch):
    monkeypatch.setattr(
        "cads_catalogue_api_service.collection_ext.query_collection",
        _static_query_collection,
    )
    response = client.get(
        "/collections/era5-something/form.json", follow_redirects=False
    )
    assert response.status_code == 307
    assert response.headers["location"] == "https://somewhere.or/s3/form.json"

    monkeypatch.setattr(
        "cads_catalogue_api_service.collection_ext.query_collection",
        _static_query_collection_nolinks,
    )
    response = client.get(
        "/collections/era5-something/form.json", follow_redirects=False
    )
    assert response.status_code == 404
    assert (
        response.json()["title"] == "Collection era5-something has no form definition"
    )


def test_ext_constraints(monkeypatch):
    monkeypatch.setattr(
        "cads_catalogue_api_service.collection_ext.query_collection",
        _static_query_collection,
    )
    response = client.get(
        "/collections/era5-something/constraints.json", follow_redirects=False
    )
    assert response.status_code == 307
    assert response.headers["location"] == "https://somewhere.or/s3/constraints.json"

    monkeypatch.setattr(
        "cads_catalogue_api_service.collection_ext.query_collection",
        _static_query_collection_nolinks,
    )
    response = client.get(
        "/collections/era5-something/constraints.json", follow_redirects=False
    )
    assert response.status_code == 404
    assert (
        response.json()["title"]
        == "Collection era5-something has no constraints definition"
    )
