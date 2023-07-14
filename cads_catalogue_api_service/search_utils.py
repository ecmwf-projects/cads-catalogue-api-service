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


def apply_filters(
    session: sa.orm.Session,
    search: sa.orm.Query,
    q: str,
    kw: list,
    portals: list[str] | None = None,
):
    """Apply allowed search filters to the running query.

    Args
    ----
        search (sqlalchemy.orm.Query): current query
        q (str): search query (full text search)
        kw (list): list of keywords query
    """
    # Always filter out hidden datasets
    search = search.filter(
        cads_catalogue.database.Resource.hidden == False  # noqa E712
    )
    # Filter by category (portal)
    if portals:
        search = search.filter(cads_catalogue.database.Resource.portal.in_(portals))

    # FT search
    if q:
        # TODO: apply weigths according to some configuration
        weight_title = 1.0
        weight_description = 0.4
        weight_fulltext = 0.2
        tsquery = sa.func.to_tsquery("english", "|".join(q.split()))
        search = search.filter(
            cads_catalogue.database.Resource.search_field.bool_op("@@")(tsquery)
        ).order_by(
            sa.func.ts_rank(
                "{0.1,%s,%s,%s}" % (weight_fulltext, weight_description, weight_title),
                cads_catalogue.database.Resource.search_field,
                tsquery,
            ).desc()
        )

    # Faceted search
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


def count_facets(
    kw_struct: dict, key: str, values: list[str], to_ignore: list[str], result: dict
) -> bool:
    """Keep count of the facets that belong to the same category as the searched keyword."""
    for k, v in kw_struct.items():
        if k in to_ignore:
            continue
        elif k == key:
            for el in v:
                result.setdefault(k, {}).setdefault(el, 0)
                result[k][el] += 1
            if not any(item in v for item in values):
                return False
        else:
            if any(item in kw_struct[key] for item in values):
                for el in v:
                    result.setdefault(k, {}).setdefault(el, 0)
                    result[k][el] += 1
    return True


def elaborate_facets(
    collections: list, k: str, v: list[str], to_ignore: list[str], result: dict
) -> list[str]:
    """
    Elaborate facets.

    Mark as "to be removed" all the collections that have nothing in common with the searched keyword,
    otherwise it keeps the count of the facets using the appropriate "count_facets" function.

    """
    to_remove = []
    for collection in collections:
        """
        Generates the structure of the keywords for each collection,
        if the collection has the category of the searched keyword ,
        the facet is counted otherwise it is added to the "to be removed" list
        """
        kw_struct = generate_keywords_structure(collection["keywords"])
        if k in kw_struct and not count_facets(kw_struct, k, v, to_ignore, result):
            to_remove.append(collection["id"])
        # if the collection does not contain the searched category, it is added to the "to remove" list
        elif k not in kw_struct:
            to_remove.append(collection["id"])
    return to_remove


def count_all(collections: list, result: dict) -> None:
    for collection in collections:
        kw_struct = generate_keywords_structure(collection["keywords"])
        for k, el in kw_struct.items():
            for v in el:
                result.setdefault(k, {}).setdefault(v, 0)
                result[k][v] += 1


def clean_result(to_ignore: list[str], result: dict) -> None:
    """Clear the results after each category count."""
    for key, value in result.items():
        if key not in to_ignore:
            result[key] = {}


def populate_facets(
    all_collections: list,
    collections: stac_fastapi.types.stac.Collections,
    keywords: list[str],
) -> CollectionsWithStats:
    """Populate the collections entity with facets."""
    to_ignore = []
    result = {}
    # generate keywords structure ES. from ["Cat1 : Kw1 "] to {'Cat1':['Kw1']}
    keywords_structure = generate_keywords_structure(keywords)
    if keywords_structure:
        for k, v in keywords_structure.items():
            to_remove = elaborate_facets(all_collections, k, v, to_ignore, result)
            # sign the category to be ignored to mantain the counted labels as they are after elaboration
            to_ignore.append(k)
            # remove all collections that are in the "to remove" list
            all_collections = list(
                filter(
                    lambda collection: collection["id"] not in to_remove,
                    all_collections,
                )
            )
            # clean the result to mantain the facets as they are until all keywords are elaborated
            if len(to_ignore) < len(keywords_structure):
                clean_result(to_ignore, result)
    # if there are no keywords, count all
    else:
        count_all(all_collections, result)
    # remove facets with no corrispondence
    result = {key: val for key, val in result.items() if val != {}}
    # sort facets alphabetically
    sorted_result = {
        k: {x: y for x, y in sorted(v.items())} for k, v in sorted(result.items())
    }
    """
    Make the result formatted as expected
    ES. from {'Cat1':{'Kw1':1}} to {'kw':[{'category':'Cat1','groups':{'Kw1':1}}]}
    """
    collections["search"] = {
        "kw": [
            {"category": cat, "groups": {kw: count for kw, count in kws.items()}}
            for cat, kws in sorted_result.items()
        ]
    }
    return collections
