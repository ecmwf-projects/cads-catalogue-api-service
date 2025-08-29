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

import cads_catalogue.database
import sqlalchemy as sa
import stac_fastapi.types
import stac_fastapi.types.stac

# TODO: this should be placed in a configuration file
WEIGHT_HIGH_PRIORITY_TERMS = 1.0
WEIGHT_TITLE = 0.8
WEIGHT_DESCRIPTION = 0.5
WEIGHT_FULLTEXT = 0.03


def apply_filters_typeahead(
    session: sa.orm.Session,
    chars: str,
    search: sa.orm.Query | None = None,
    portals: list[str] | None = None,
    limit: int | None = None,
):
    """Apply filters to return words matching initial input characters, as suggestions for searching datasets.

    Args:
        session: sqlalchemy session object
        chars: initial characters of the words to find
        search: current dataset query
        portals: list of datasets portals to consider
        limit: if specified, limit length of resulting words
    """
    if search is None:
        search = session.query(cads_catalogue.database.Resource)
    search = search.filter(
        cads_catalogue.database.Resource.hidden == False  # noqa E712
    )
    if portals:
        search = search.filter(cads_catalogue.database.Resource.portal.in_(portals))
    g = sa.func.unnest(
        sa.func.string_to_array(
            sa.func.lower(cads_catalogue.database.Resource.title), " "
        )
    ).label("g")
    t = search.with_entities(g).scalar_subquery().alias("t")
    suggestion = sa.func.unnest(sa.func.array_agg(sa.func.distinct(t.c.g))).label(
        "suggestion"
    )
    tt = session.query(suggestion).select_from(t).scalar_subquery().alias("tt")
    # consider only (resulting words with length > 2) AND (words starting with chars):
    filter = sa.and_(
        sa.func.length(tt.c.suggestion).__gt__(2), tt.c.suggestion.ilike(chars + "%")
    )
    search = (
        session.query(tt.c.suggestion)
        .select_from(tt)
        .filter(filter)
        .order_by(tt.c.suggestion)
    )
    if limit is not None:
        search = search.limit(limit)  # type: ignore

    # final sql for `apply_filters_typeahead(session, 'er', portals=['cams', 'c3s'], limit=10)`:
    # SELECT suggestion FROM
    # (
    #     SELECT unnest(array_agg(distinct(t.g))) AS suggestion FROM
    #     (
    #         SELECT unnest(string_to_array(lower(title), ' ')) AS g FROM resources
    #         WHERE resources.hidden = true AND resources.portal IN ('cams', 'c3s')
    #     )
    #      AS t
    # ) AS tt
    # WHERE length(tt.suggestion) > 2 AND tt.suggestion ILIKE 'er%'
    # ORDER BY tt.suggestion
    # LIMIT 10;

    return search


def split_by_category(keywords: list) -> list:
    """Given a list of keywords composed by a "category: value", split them in multiple lists.

    Splitting is based on the category.
    """
    categories: dict = {}
    for keyword in keywords:
        category, value = keyword.split(":", 1)
        if category not in categories:
            categories[category] = []
        categories[category].append(":".join([category, value]))
    return list(categories.values())


def generate_ts_query(q: str = ""):
    """Generate the string tokenizer from query string.

    Parameters
    ----------
    q : str, optional
        query string, as read from the API request

    Returns
    -------
    SQL Function expression
        Tokenized expression used for the full text search or sorting
    """
    return sa.func.websearch_to_tsquery("english", q.replace("'", '"'))


def fulltext_order_by(q: str):
    """Generate the full text search order by clause."""
    tsquery = generate_ts_query(q)
    return sa.func.ts_rank2(
        "{%s,%s,%s,%s}"
        % (
            # NOTE: order of weights follows {D,C,B,A} labelling of 'search_field' of table resources
            WEIGHT_HIGH_PRIORITY_TERMS,
            WEIGHT_FULLTEXT,
            WEIGHT_DESCRIPTION,
            WEIGHT_TITLE,
        ),
        cads_catalogue.database.Resource.search_field,
        cads_catalogue.database.Resource.fts,
        tsquery,
        sa.func.coalesce(cads_catalogue.database.Resource.popularity, 1),
    ).desc()


def apply_filters(
    session: sa.orm.Session,
    search: sa.orm.Query,
    q: str | None,
    kw: list | None,
    idx: list | None,
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

    if idx:
        search = search.filter(cads_catalogue.database.Resource.resource_uid.in_(idx))

    # Faceted search
    if kw:
        # Facetes search criteria is to run on OR in the same category, and AND between categories
        # To make this working be perform subqueryes joint with the INTERSECT operator
        splitted_categories = split_by_category(kw)

        subqueries = []
        for categorized in splitted_categories:
            # 1. Filter by all keywords in this category
            query_kw = (
                session.query(cads_catalogue.database.Facet.facet_id)
                # We cannot just use in_ on all kws because we need to AND on different
                .filter(cads_catalogue.database.Facet.facet_name.in_(categorized))
            )
            # 2. Manually build many to many relation
            subquery_mtm = (
                session.query(cads_catalogue.database.ResourceFacet.resource_id)
                .filter(cads_catalogue.database.ResourceFacet.facet_id.in_(query_kw))
                .scalar_subquery()
            )
            # 3. Perform partial query
            subquery = session.query(cads_catalogue.database.Resource).filter(
                cads_catalogue.database.Resource.resource_id.in_(subquery_mtm)
            )
            subqueries.append(subquery)
        # 4. Join all subqueries with INTERSECT
        search = search.intersect(*subqueries)

    # FT search
    if q:
        tsquery = generate_ts_query(q)
        search = search.filter(
            cads_catalogue.database.Resource.search_field.bool_op("@@")(tsquery)
        )
    return search


class CollectionsWithStats(stac_fastapi.types.stac.Collections):
    """A collection with search stats."""

    search: dict[str, Any]


def generate_keywords_structure(keywords: list[str] | None) -> dict[str, Any]:
    """Generate a structure with the categories and keywords.

    Structure in build upon given a list of keywords (semicolon separated).
    """
    keywords_structure: dict = {}
    if keywords:
        for kw in keywords:
            category, keyword = [x.strip() for x in kw.split(":")]
            keywords_structure.setdefault(category, []).append(keyword)
    return keywords_structure


def count_facets(
    key: str, values: list[str], kw_struct: dict, result: dict, id: str, to_remove: list
) -> None:
    for k, v in kw_struct.items():
        if k == key or any(item in kw_struct[key] for item in values):
            for el in v:
                result.setdefault(k, {}).setdefault(el, 0)
                result[k][el] += 1
            if not any(item in kw_struct[key] for item in values):
                to_remove.append(id)
        if k == key and not any(item in kw_struct[key] for item in values):
            to_remove.append(id)


def count_collection_facets(
    collections: list, k: str, v: list[str], result: dict
) -> list[str]:
    to_remove: list = []
    for collection in collections:
        kw_struct = generate_keywords_structure(collection["keywords"])
        if k in kw_struct:
            count_facets(k, v, kw_struct, result, collection["id"], to_remove)
        else:
            to_remove.append(collection["id"])
    return to_remove


def count_all(collections: list, result: dict) -> None:
    for collection in collections:
        kw_struct = generate_keywords_structure(collection["keywords"])
        for k, el in kw_struct.items():
            for v in el:
                result.setdefault(k, {}).setdefault(v, 0)
                result[k][v] += 1


def populate_facets(
    all_collections: list,
    collections: CollectionsWithStats,
    keywords: list[str] | None,
) -> CollectionsWithStats:
    """Populate the collections entity with facets."""
    result: dict = {}
    # generate keywords structure ES. from ["Cat1 : Kw1 "] to {'Cat1':['Kw1']}
    keywords_structure = generate_keywords_structure(keywords)
    if keywords_structure:
        for index, (k, v) in enumerate(keywords_structure.items()):
            to_remove = count_collection_facets(all_collections, k, v, result)
            all_collections = list(
                filter(
                    lambda collection: collection["id"] not in to_remove,
                    all_collections,
                )
            )
            if index + 1 < len(keywords_structure.items()):
                result.clear()
    else:
        count_all(all_collections, result)
    result = {key: val for key, val in result.items() if val != {}}
    sorted_result = {
        k: {x: y for x, y in sorted(v.items())} for k, v in sorted(result.items())
    }

    # Make the result formatted as expected
    # ES. from {'Cat1':{'Kw1':1}} to {'kw':[{'category':'Cat1','groups':{'Kw1':1}}]}
    collections["search"] = {
        "kw": [
            {"category": cat, "groups": {kw: count for kw, count in kws.items()}}
            for cat, kws in sorted_result.items()
        ]
    }
    return collections
