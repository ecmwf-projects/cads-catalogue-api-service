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

import sqlalchemy as sa
from testing import get_record

import cads_catalogue_api_service.client
import cads_catalogue_api_service.extensions


class FakeQuery:
    def order_by(self, order_by):
        self.order_by = order_by
        return self

    def limit(self, limit: int):
        self.limit = limit
        return self

    def offset(self, offset: int):
        self.offset = offset
        return self


def test_apply_sorting() -> None:
    query = FakeQuery()
    search = cads_catalogue_api_service.client.apply_sorting_and_limit(
        query, q="", sortby="id", page=2, limit=10
    )

    assert search.limit == 10
    assert search.offset == 20
    assert search.order_by.element.key == "resource_uid"

    query = FakeQuery()
    search = cads_catalogue_api_service.client.apply_sorting_and_limit(
        query, q="foo", sortby="relevance", page=0, limit=10
    )

    assert search.limit == 10
    assert search.offset == 0
    assert search.order_by.element.name == "ts_rank"


def test_get_next_prev_links() -> None:
    next_prev_links = cads_catalogue_api_service.client.get_next_prev_links(
        sortby=cads_catalogue_api_service.extensions.CatalogueSortCriterion.id_asc,
        page=0,
        limit=10,
        count=100,
    )

    assert next_prev_links.get("next") == {
        "limit": 10,
        "page": 1,
        "sortby": cads_catalogue_api_service.extensions.CatalogueSortCriterion.id_asc.value,
    }
    assert next_prev_links.get("prev") is None

    next_prev_links = cads_catalogue_api_service.client.get_next_prev_links(
        sortby=cads_catalogue_api_service.extensions.CatalogueSortCriterion.id_asc,
        page=2,
        limit=10,
        count=100,
    )

    assert next_prev_links.get("prev") == {
        "limit": 10,
        "page": 1,
        "sortby": cads_catalogue_api_service.extensions.CatalogueSortCriterion.id_asc.value,
    }
    assert next_prev_links.get("next") == {
        "limit": 10,
        "page": 3,
        "sortby": cads_catalogue_api_service.extensions.CatalogueSortCriterion.id_asc.value,
    }

    next_prev_links = cads_catalogue_api_service.client.get_next_prev_links(
        sortby=cads_catalogue_api_service.extensions.CatalogueSortCriterion.id_asc,
        page=9,
        limit=10,
        count=100,
    )

    assert next_prev_links.get("prev") == {
        "limit": 10,
        "page": 8,
        "sortby": cads_catalogue_api_service.extensions.CatalogueSortCriterion.id_asc.value,
    }
    assert next_prev_links.get("next") is None

    next_prev_links = cads_catalogue_api_service.client.get_next_prev_links(
        sortby=cads_catalogue_api_service.extensions.CatalogueSortCriterion.id_asc,
        page=9,
        limit=10,
        count=96,
    )

    assert next_prev_links.get("prev") == {
        "limit": 10,
        "page": 8,
        "sortby": cads_catalogue_api_service.extensions.CatalogueSortCriterion.id_asc.value,
    }
    assert next_prev_links.get("next") is None


def test_get_sorting_clause():
    record = get_record(id="foo-bar")

    assert cads_catalogue_api_service.client.get_sorting_clause(record, sort="id") == (
        record.resource_uid,
        sa.asc,
    )
    assert cads_catalogue_api_service.client.get_sorting_clause(
        record, sort="updated"
    ) == (
        record.resource_update,
        sa.desc,
    )
    # Default
    assert cads_catalogue_api_service.client.get_sorting_clause(
        record, sort="foobarbaz"
    ) == (
        record.resource_update,
        sa.desc,
    )
