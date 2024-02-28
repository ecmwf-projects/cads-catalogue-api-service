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

# type: ignore

from typing import Any

import cads_catalogue_api_service.client


class FakeQuery:
    def order_by(self, order_by):
        self.order_by = order_by
        return self

    def limit(self, limit: int):
        self.limit = limit
        return self


class MockObj:
    def __init__(self, value: int):
        self.value = str(value)

    def __getattribute__(self, __name: str) -> Any:
        if __name != "value":
            global called_key
            called_key = self.value
            return self.value
        return super().__getattribute__(__name)


called_key = None


class MockSortBy:
    def __init__(self, value: str):
        self.value = value

    @property
    def key(self):
        return self.value


def test_get_cursor_compare_criteria() -> None:
    # unknown criteria
    assert (
        cads_catalogue_api_service.client.get_cursor_compare_criteria(sortby="foo")
        == "__ge__"
    )
    assert (
        cads_catalogue_api_service.client.get_cursor_compare_criteria(
            sortby="foo", back=True
        )
        == "__lt__"
    )
    # asc criteria
    assert (
        cads_catalogue_api_service.client.get_cursor_compare_criteria(sortby="id")
        == "__ge__"
    )
    assert (
        cads_catalogue_api_service.client.get_cursor_compare_criteria(
            sortby="id", back=True
        )
        == "__lt__"
    )
    # desc criteria
    assert (
        cads_catalogue_api_service.client.get_cursor_compare_criteria(sortby="update")
        == "__le__"
    )
    assert (
        cads_catalogue_api_service.client.get_cursor_compare_criteria(
            sortby="update", back=True
        )
        == "__gt__"
    )


def test_apply_sorting() -> None:
    query = FakeQuery()

    search, sort_by = cads_catalogue_api_service.client.apply_sorting_and_limit(
        query, sortby="id", cursor=None, limit=10
    )
    assert sort_by.key == "resource_uid"
    assert search.limit == 11


def test_get_next_prev_links() -> None:
    collections = [MockObj(v) for v in range(1, 17)]

    next_prev_links = cads_catalogue_api_service.client.get_next_prev_links(
        collections=collections[0:11], sort_by=MockSortBy("id"), cursor=None, limit=10
    )

    assert next_prev_links.get("next") == {"cursor": "MTE="}
    assert next_prev_links.get("prev") is None
    assert called_key == "11"

    next_prev_links = cads_catalogue_api_service.client.get_next_prev_links(
        collections=collections[2:13], sort_by=MockSortBy("id"), cursor="2", limit=10
    )

    assert next_prev_links.get("next") == {"cursor": "MTM="}
    assert next_prev_links.get("prev") == {"back": "true", "cursor": "Mw=="}
    assert called_key == "3"

    next_prev_links = cads_catalogue_api_service.client.get_next_prev_links(
        collections=collections[2:13],
        sort_by=MockSortBy("id"),
        cursor="2",
        limit=10,
        back=True,
    )

    assert next_prev_links.get("next") == {"cursor": "Mg=="}
    assert next_prev_links.get("prev") == {"back": "true", "cursor": "MTI="}
    assert called_key == "12"

    next_prev_links = cads_catalogue_api_service.client.get_next_prev_links(
        collections=collections[0:4],
        sort_by=MockSortBy("id"),
        cursor=None,
        limit=10,
    )

    assert next_prev_links.get("next") is None
    assert next_prev_links.get("prev") is None

    next_prev_links = cads_catalogue_api_service.client.get_next_prev_links(
        collections=collections[2:6],
        sort_by=MockSortBy("id"),
        cursor="2",
        limit=10,
        back=True,
    )

    assert next_prev_links.get("next") == {"cursor": "Mg=="}
    assert next_prev_links.get("prev") == {"back": "true", "cursor": "Ng=="}
