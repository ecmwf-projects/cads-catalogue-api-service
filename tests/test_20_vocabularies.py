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


def static_licences_query(_foo: Any) -> list[cads_catalogue.database.Licence]:
    return [
        cads_catalogue.database.Licence(
            licence_id=1, licence_uid="cc-by-4.0", title="CC-BY-4.0", revision=1
        ),
        cads_catalogue.database.Licence(
            licence_id=3, licence_uid="cc-by-sa-4.0", title="CC-BY-SA-4.0", revision=2
        ),
    ]


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
            {"id": "cc-by-4.0", "label": "CC-BY-4.0", "revision": 1},
            {"id": "cc-by-sa-4.0", "label": "CC-BY-SA-4.0", "revision": 2},
        ],
    }
