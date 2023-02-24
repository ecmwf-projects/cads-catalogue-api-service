"""Search related utilities."""

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

import cads_catalogue.faceted_search
import sqlalchemy as sa
import stac_fastapi.types


class CollectionsWithStats(stac_fastapi.types.stac.Collections):
    """A collection with search stats."""

    search: dict[str, Any]


def generate_keywords_structure(keywords: list[str]) -> dict[str, Any]:
    """Generate a structure with the categories and keywords.

    Structure in build upon given a list of keywords (semicolon separated).
    """
    keywords_structure = {}
    for kw in keywords:
        category, keyword = [x.strip() for x in kw.split(":")]
        keywords_structure.setdefault(category, []).append(keyword)
    return keywords_structure


def populate_facets(
    session: sa.orm.Session,
    collections: stac_fastapi.types.stac.Collections,
    search: sa.orm.Query,
    keywords: list[str],
) -> CollectionsWithStats:
    """Populate the collections entity with facets."""
    search.all()

    keywords_structure = generate_keywords_structure(keywords)
    dataset_kw_grouping = cads_catalogue.faceted_search.get_datasets_by_keywords(
        search, keywords_structure
    )
    results_ids = [d.resource_id for d in dataset_kw_grouping]
    faceted_stats = cads_catalogue.faceted_search.get_faceted_stats(
        session, results_ids
    )

    facets = {}
    for kw in faceted_stats:
        category_name = kw["category_name"]
        category_value = kw["category_value"]
        count = kw["count"]
        facets.setdefault(category_name, {})[category_value] = count

    collections["search"] = {
        "kw": [
            {"category": cat, "groups": {kw: count for kw, count in kws.items()}}
            for cat, kws in facets.items()
        ]
    }
    return collections
