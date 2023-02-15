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

from cads_catalogue_api_service.search_utils import (
    CollectionsWithStats,
    populate_facets,
)


def test_populate_facets():
    """Test populate_facets."""

    class MockSearch:
        """Mock the search."""

        def all(self):
            """Mock the all method."""
            return [
                MockResult(["cat1:kw1", "cat1:kw2"]),
                MockResult(["cat1:kw1", "cat2:kw3"]),
                MockResult(["cat1:kw2", "cat2:kw3"]),
            ]

    class MockResult:
        """Mock the result."""

        def __init__(self, keywords):
            """Init."""
            self.keywords = keywords

    search = MockSearch()
    collections = CollectionsWithStats()
    collections = populate_facets(search, collections)
    assert collections["search"] == {
        "kw": [
            {"category": "cat1", "groups": {"kw1": None, "kw2": None}},
            {"category": "cat2", "groups": {"kw3": None}},
        ]
    }
