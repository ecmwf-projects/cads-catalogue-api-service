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

import datetime
from typing import Any

import fastapi
import fastapi.testclient
from cads_catalogue import database

from cads_catalogue_api_service.main import app

client = fastapi.testclient.TestClient(app)

STATIC_DATASET = database.Resource(
    resource_id=1,
    resource_uid="foo-bar-baz",
    title="Foo bar baz",
)

STATIC_RESULTS = [
    database.Content(
        content_id=1,
        slug="copernicus-interactive-climates-atlas",
        content_update=datetime.datetime(2022, 1, 1),
        description="Foo bar baz",
        image="relative/to/somrthing.png",
        link="http://apprepo.org/app-1",
        publication_date=datetime.datetime(2022, 1, 1),
        site="cds",
        title="Copernicus Interactive Climate Atlas",
        type="application",
        resources=[STATIC_DATASET],
    ),
    database.Content(
        content_id=2,
        slug="how-to-api",
        content_update=datetime.datetime(2022, 1, 1),
        data=None,
        description="For bar baz qux",
        layout="relative/to/something.json",
        publication_date=datetime.datetime(2022, 1, 1),
        site="cds",
        title="How to API?",
        type="page",
    ),
    database.Content(
        content_id=3,
        slug="how-to-api",
        content_update=datetime.datetime(2022, 1, 1),
        data=None,
        description="For bar baz qux",
        layout="relative/to/something.json",
        publication_date=datetime.datetime(2022, 1, 1),
        site="ads",
        title="How to API?",
        type="page",
    ),
]


def static_query_contents(
    session: Any,
    site: str,
    ctype: str | None = None,
):
    results = (
        STATIC_RESULTS
        if not site
        else [
            c
            for c in STATIC_RESULTS
            if c.site == site and (not ctype or c.type == ctype)
        ]
    )

    if ctype and not results:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Content type {ctype} not implemented",
        )

    return (
        len(results),
        results,
    )


def static_query_content(
    session: Any,
    site: str,
    ctype: str,
    id: str,
):
    results = [
        c
        for c in STATIC_RESULTS
        if c.site == site and (not ctype or c.type == ctype) and c.slug == id
    ]

    if results:
        return results[0]

    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_404_NOT_FOUND,
        detail=f"Content {id} of type {ctype} not found",
    )


def test_all_contents(monkeypatch) -> None:
    monkeypatch.setattr(
        "cads_catalogue_api_service.contents.query_contents",
        static_query_contents,
    )
    response = client.get("/contents")

    assert response.status_code == 200

    results = response.json()

    assert results["count"] == 3
    assert len([c for c in results["contents"] if c["type"] == "application"]) == 1
    assert len([c for c in results["contents"] if c["type"] == "page"]) == 2

    # with site header
    response = client.get("/contents", headers={"X-CADS-SITE": "cds"})

    assert response.status_code == 200

    results = response.json()

    assert results["count"] == 2
    assert len([c for c in results["contents"] if c["type"] == "application"]) == 1
    assert len([c for c in results["contents"] if c["type"] == "page"]) == 1


def test_ctype_contents(monkeypatch) -> None:
    monkeypatch.setattr(
        "cads_catalogue_api_service.contents.query_contents",
        static_query_contents,
    )

    response = client.get("/contents/page", headers={"X-CADS-SITE": "cds"})

    assert response.status_code == 200

    results = response.json()
    assert results["count"] == 1
    assert len([c for c in results["contents"] if c["type"] == "page"]) == 1

    response = client.get("/contents/foo", headers={"X-CADS-SITE": "cds"})

    assert response.status_code == 501


def test_query_content(monkeypatch) -> None:
    monkeypatch.setattr(
        "cads_catalogue_api_service.contents.query_content",
        static_query_content,
    )

    response = client.get("/contents/page/bbbb", headers={"X-CADS-SITE": "cds"})

    assert response.status_code == 404

    response = client.get("/contents/page/how-to-api", headers={"X-CADS-SITE": "cds"})

    assert response.status_code == 200

    results = response.json()
    assert results["title"] == "How to API?"


def test_links(monkeypatch) -> None:
    monkeypatch.setattr(
        "cads_catalogue_api_service.contents.query_content",
        static_query_content,
    )

    response = client.get("/contents/page/how-to-api", headers={"X-CADS-SITE": "cds"})

    assert response.status_code == 200

    result = response.json()
    assert result["title"] == "How to API?"
    assert result["links"][0]["href"] == "http://testserver/contents/page"
    assert result["links"][1]["href"] == "http://testserver/contents/page/how-to-api"
    assert result["links"][0]["rel"] == "parent"
    assert result["links"][1]["rel"] == "self"


def test_links_relations(monkeypatch) -> None:
    monkeypatch.setattr(
        "cads_catalogue_api_service.contents.query_content",
        static_query_content,
    )

    response = client.get(
        "/contents/application/copernicus-interactive-climates-atlas",
        headers={"X-CADS-SITE": "cds"},
    )

    assert response.status_code == 200

    result = response.json()
    assert result["title"] == "Copernicus Interactive Climate Atlas"
    assert len([link for link in result["links"] if link.get("rel") == "related"]) > 0
    related = [link for link in result["links"] if link.get("rel") == "related"][0]
    assert related["href"] == "http://testserver/collections/foo-bar-baz"
    assert related["rel"] == "related"
    assert related["title"] == "Foo bar baz"
