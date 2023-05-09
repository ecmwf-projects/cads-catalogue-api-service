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


def split_by_category(keywords: list) -> list:
    """Given a list of keywords composed by a "category: value", split them in multiple lists.

    Splitting is based on the category.
    """
    categories = {}
    for keyword in keywords:
        category, value = keyword.split(":", 1)
        if category not in categories:
            categories[category] = []
        categories[category].append(":".join([category, value]))
    return list(categories.values())


def apply_filters(session: sa.orm.Session, search: sa.orm.Query, q: str, kw: list):
    """Apply allowed search filters to the running query.

    Args
    ----
        search (sqlalchemy.orm.Query): current query
        q (str): search query (full text search)
        kw (list): list of keywords query
    """
    if q:
        tsquery = sa.func.plainto_tsquery("english", q)
        search = search.filter(
            cads_catalogue.database.Resource.fulltext_tsv.bool_op("@@")(tsquery)
        ).order_by(
            sa.func.ts_rank(
                cads_catalogue.database.Resource.fulltext_tsv, tsquery
            ).desc()
        )

    if kw:
        # Facetes search criteria is to run on OR in the same category, and AND between categories
        # To make this working be perform subqueryes joint with the INTERSECT operator
        splitted_categories = split_by_category(kw)

        subqueries = []
        for categorized in splitted_categories:
            # 1. Filter by all keywords in this category
            query_kw = (
                session.query(cads_catalogue.database.Keyword.keyword_id)
                # We cannot just use in_ on all kws because we need to AND on different
                .filter(cads_catalogue.database.Keyword.keyword_name.in_(categorized))
            )
            # 2. Manually build many to many relation
            subquery_mtm = (
                session.query(cads_catalogue.database.ResourceKeyword.resource_id)
                .filter(
                    cads_catalogue.database.ResourceKeyword.keyword_id.in_(query_kw)
                )
                .scalar_subquery()
            )
            # 3. Perform partial query
            subquery = session.query(cads_catalogue.database.Resource).filter(
                cads_catalogue.database.Resource.resource_id.in_(subquery_mtm)
            )
            subqueries.append(subquery)

        # 4. Join all subqueries with INTERSECT
        search = search.intersect(*subqueries)

    return search


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


def read_facets(session: sa.orm.Session, search: sa.orm.Query, keywords: list[str]):
    keywords_structure = generate_keywords_structure(keywords)
    dataset_kw_grouping = cads_catalogue.faceted_search.get_datasets_by_keywords(
        search, keywords_structure
    )
    results_ids = [d.resource_id for d in dataset_kw_grouping]
    faceted_stats = cads_catalogue.faceted_search.get_faceted_stats(
        session, results_ids
    )

    facets = {}
    for category_name, category_value, count in faceted_stats:
        facets.setdefault(category_name, {})[category_value] = count
    return facets


def populate_facets(
    session: sa.orm.Session,
    collections: stac_fastapi.types.stac.Collections,
    search: sa.orm.Query,
    keywords: list[str],
) -> CollectionsWithStats:
    """Populate the collections entity with facets."""
    facets = read_facets(session, search, keywords)
    collections["search"] = {
        "kw": [
            {"category": cat, "groups": {kw: count for kw, count in kws.items()}}
            for cat, kws in facets.items()
        ]
    }
    return collections
