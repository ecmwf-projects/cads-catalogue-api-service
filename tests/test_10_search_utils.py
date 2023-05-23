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


import fastapi
import fastapi.testclient

from cads_catalogue_api_service.main import app
from cads_catalogue_api_service.search_utils import (
    populate_facets,
)

client = fastapi.testclient.TestClient(app)


def test_populate_facets(monkeypatch):
    """Test populate_facets."""
    all_collections = [
        {"id": "dataset1", "keywords": ["cat1: kw1"]},
        {"id": "dataset2", "keywords": ["cat1: kw1", "cat1: kw2"]},
        {"id": "dataset3", "keywords": ["cat2: kw1"]},
        {"id": "dataset4", "keywords": ["cat1: kw2", "cat2: kw1"]},
    ]

    collections = {
        "collections": [
            {"id": "dataset1", "keywords": ["cat1: kw1"]},
            {"id": "dataset2", "keywords": ["cat1: kw1", "cat1: kw2"]},
            {"id": "dataset3", "keywords": ["cat2: kw1"]},
            {"id": "dataset4", "keywords": ["cat1: kw2", "cat2: kw1"]},
        ]
    }

    result = populate_facets(
        all_collections=all_collections, collections=collections, keywords=[]
    )
    assert result["search"] == {
        "kw": [
            {"category": "cat1", "groups": {"kw1": 2, "kw2": 2}},
            {"category": "cat2", "groups": {"kw1": 2}},
        ]
    }

    result = populate_facets(
        all_collections=all_collections, collections=collections, keywords=["cat1: kw1"]
    )
    assert result["search"] == {
        "kw": [{"category": "cat1", "groups": {"kw1": 2, "kw2": 2}}]
    }

    result = populate_facets(
        all_collections=all_collections, collections=collections, keywords=["cat2: kw1"]
    )
    assert result["search"] == {
        "kw": [
            {"category": "cat2", "groups": {"kw1": 2}},
            {"category": "cat1", "groups": {"kw2": 1}},
        ]
    }
