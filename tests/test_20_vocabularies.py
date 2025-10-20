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
import pytest

import cads_catalogue_api_service
from cads_catalogue_api_service import vocabularies
from cads_catalogue_api_service.main import app

client = fastapi.testclient.TestClient(app)


TEST_DATA = [
    cads_catalogue.database.Licence(
        licence_id=1,
        licence_uid="cc-by-4.0",
        title="CC-BY-4.0",
        revision=1,
        md_filename="cc-by-4.0-1.md",
        download_filename="cc-by-4.0-1.pdf",
        scope="dataset",
        spdx_identifier="CC-BY-4.0",
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


def static_licences_query(
    _foo: Any, scope: str = "dataset", portals: list[str] | None = None
) -> list[cads_catalogue.database.Licence]:
    return TEST_DATA


def static_licence_query(
    _foo: Any, licence_uid: str
) -> cads_catalogue.database.Licence:
    return TEST_DATA[0]


KEYWORDS = [
    "Provider: Copernicus C3S",
    "Product type: Reanalysis",
    "Variable domain: Land (physics)",
    "Product type: Derived reanalysis",
]


class Facet:
    def __init__(self, facet_name: str):
        self.facet_name = facet_name


def static_keywords_licence(_foo: Any) -> list[cads_catalogue.database.Facet]:
    return [Facet(facet_name=kw) for kw in KEYWORDS]


def get_session() -> None:
    """Mock session generation."""
    return None


app.dependency_overrides[cads_catalogue_api_service.dependencies.get_session] = (
    get_session
)


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
                "portal": None,
                "revision": 1,
                "attachment_url": "/document-storage/cc-by-4.0-1.pdf",
                "contents_url": "/document-storage/cc-by-4.0-1.md",
                "scope": "dataset",
                "spdx_identifier": "CC-BY-4.0",
            },
            {
                "id": "cc-by-sa-4.0",
                "label": "CC-BY-SA-4.0",
                "portal": None,
                "revision": 2,
                "attachment_url": "/document-storage/cc-by-4.0-2.pdf",
                "contents_url": "/document-storage/cc-by-4.0-2.md",
                "scope": "dataset",
                "spdx_identifier": None,
            },
        ],
    }


def test_vocabulary_license(monkeypatch) -> None:
    monkeypatch.setattr(
        "cads_catalogue_api_service.vocabularies.query_licence",
        static_licence_query,
    )
    """Test list of licences."""
    response = client.get(
        "/vocabularies/licences/cc-by-4.0",
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": "cc-by-4.0",
        "label": "CC-BY-4.0",
        "revision": 1,
        "portal": None,
        "attachment_url": "/document-storage/cc-by-4.0-1.pdf",
        "contents_url": "/document-storage/cc-by-4.0-1.md",
        "scope": "dataset",
        "spdx_identifier": "CC-BY-4.0",
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


@pytest.mark.parametrize(
    ("scope", "portals", "expected"),
    [
        (
            vocabularies.LicenceScopeCriterion.all,
            ["portal-a"],
            {"dataset-used", "portal-a"},
        ),
        (
            vocabularies.LicenceScopeCriterion.dataset,
            ["portal-a"],
            {"dataset-used"},
        ),
        (
            vocabularies.LicenceScopeCriterion.portal,
            ["portal-a"],
            {"portal-a"},
        ),
    ],
)
def test_query_licences(session_obj, scope, portals, expected) -> None:
    """Licences query should filter portals and unused dataset licences."""
    session = session_obj()
    try:
        resource = cads_catalogue.database.Resource(
            resource_uid="resource-1",
            abstract="A dataset resource",
            description={"en": {"description": "Example"}},
            type="dataset",
        )
        linked_dataset_licence = cads_catalogue.database.Licence(
            licence_uid="dataset-used",
            title="Dataset Licence Used",
            revision=1,
            md_filename="used.md",
            download_filename="used.pdf",
            scope="dataset",
        )
        unlinked_dataset_licence = cads_catalogue.database.Licence(
            licence_uid="dataset-unused",
            title="Dataset Licence Unused",
            revision=1,
            md_filename="unused.md",
            download_filename="unused.pdf",
            scope="dataset",
        )
        portal_a_licence = cads_catalogue.database.Licence(
            licence_uid="portal-a",
            title="Portal Licence A",
            revision=1,
            md_filename="portal.md",
            download_filename="portal.pdf",
            scope="portal",
            portal="portal-a",
        )
        portal_b_licence = cads_catalogue.database.Licence(
            licence_uid="portal-b",
            title="Portal Licence B",
            revision=1,
            md_filename="portal-other.md",
            download_filename="portal-other.pdf",
            scope="portal",
            portal="portal-b",
        )

        session.add_all(
            [
                resource,
                linked_dataset_licence,
                unlinked_dataset_licence,
                portal_a_licence,
                portal_b_licence,
            ]
        )
        session.flush()

        link = cads_catalogue.database.ResourceLicence(
            resource_id=resource.resource_id,
            licence_id=linked_dataset_licence.licence_id,
        )
        session.add(link)
        session.commit()

        results = vocabularies.query_licences(session, scope, portals).all()

        returned_uids = {row.licence_uid for row in results}
        assert returned_uids == expected
    finally:
        session.close()
