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

from typing import Any

import cads_catalogue
import fastapi
import fastapi.testclient

import cads_catalogue_api_service
from cads_catalogue_api_service.main import app

client = fastapi.testclient.TestClient(app)


def static_licences_query(
    _foo: Any, scope: str = "dataset"
) -> list[cads_catalogue.database.Licence]:
    return [
        cads_catalogue.database.Licence(
            licence_id=1,
            licence_uid="cc-by-4.0",
            title="CC-BY-4.0",
            revision=1,
            md_filename="cc-by-4.0-1.md",
            download_filename="cc-by-4.0-1.pdf",
            scope="dataset",
        ),
        cads_catalogue.database.Licence(
            licence_id=3,
            licence_uid="cc-by-sa-4.0",
            title="CC-BY-SA-4.0",
            revision=2,
            md_filename="cc-by-4.0-2.md",
            download_filename="cc-by-4.0-2.pdf",
            scope="dataset",
        ),
    ]


KEYWORDS = [
    "Provider: Copernicus C3S",
    "Product type: Reanalysis",
    "Variable domain: Land (physics)",
    "Product type: Derived reanalysis",
]


class Keyword:
    def __init__(self, keyword_name: str):
        self.keyword_name = keyword_name


def static_keywords_licence(_foo: Any) -> list[cads_catalogue.database.Keyword]:
    return [Keyword(keyword_name=kw) for kw in KEYWORDS]


def get_session() -> None:
    """Mock session generation."""
    return None


app.dependency_overrides[
    cads_catalogue_api_service.dependencies.get_session
] = get_session


def test_vocabularies_license(monkeypatch) -> None:
    monkeypatch.setattr(
        "cads_catalogue_api_service.vocabularies.query_licences",
        static_licences_query,
    )
    """Test list of licences."""
    response = client.get(
        "/vocabularies/licences",
    )

    assert response.status_code == 200
    assert response.json() == {
        "licences": [
            {
                "id": "cc-by-4.0",
                "label": "CC-BY-4.0",
                "revision": 1,
                "attachment_url": "/document-storage/cc-by-4.0-1.pdf",
                "contents_url": "/document-storage/cc-by-4.0-1.md",
                "scope": "dataset",
            },
            {
                "id": "cc-by-sa-4.0",
                "label": "CC-BY-SA-4.0",
                "revision": 2,
                "attachment_url": "/document-storage/cc-by-4.0-2.pdf",
                "contents_url": "/document-storage/cc-by-4.0-2.md",
                "scope": "dataset",
            },
        ],
    }


def test_vocabularies_keywords(monkeypatch) -> None:
    monkeypatch.setattr(
        "cads_catalogue_api_service.vocabularies.query_keywords",
        static_keywords_licence,
    )
    """Test list of keywords."""
    response = client.get(
        "/vocabularies/keywords",
    )

    assert response.status_code == 200
    assert response.json() == {
        "keywords": [{"id": kw, "label": kw} for kw in KEYWORDS],
    }
