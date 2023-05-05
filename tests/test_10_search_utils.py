# Copyright 2023, European Union.
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

import cads_catalogue_api_service
from cads_catalogue_api_service.main import app
from cads_catalogue_api_service.search_utils import (
    CollectionsWithStats,
    populate_facets,
)

client = fastapi.testclient.TestClient(app)


def mock_read_facets(session: Any, search: Any, keywords: list[str]) -> Any:
    """Mock session generation."""
    return {"cat1": {"kw1": None, "kw2": None}, "cat2": {"kw3": None}}


app.dependency_overrides[
    cads_catalogue_api_service.search_utils.read_facets
] = mock_read_facets


def test_populate_facets(monkeypatch):
    """Test populate_facets."""

    class MockSearch:
        """Mock the search."""

        def all(self):
            """Mock the all method."""
            return [
                MockResult(["cat1:kw1", "cat1:kw2"], 1),
                MockResult(["cat1:kw1", "cat2:kw3"], 2),
                MockResult(["cat1:kw2", "cat2:kw3"], 3),
            ]

        def __iter__(self):
            for each in self.all():
                yield each

    class MockResult:
        """Mock the result."""

        def __init__(self, keywords, resource_id):
            """Init."""
            self.keywords = keywords
            self.resource_id = resource_id

    monkeypatch.setattr(
        "cads_catalogue_api_service.search_utils.read_facets", mock_read_facets
    )

    search = MockSearch()
    collections = CollectionsWithStats()
    collections = populate_facets(
        session=None, collections=collections, search=search, keywords=[]
    )
    assert collections["search"] == {
        "kw": [
            {"category": "cat1", "groups": {"kw1": None, "kw2": None}},
            {"category": "cat2", "groups": {"kw3": None}},
        ]
    }
