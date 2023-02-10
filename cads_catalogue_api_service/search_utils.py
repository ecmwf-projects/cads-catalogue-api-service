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

import itertools
from typing import Any

import sqlalchemy as sa
import stac_fastapi.types


class CollectionsWithStats(stac_fastapi.types.stac.Collections):
    """A collection with search stats."""

    search: dict[str, Any]


# FIXME: this is just a provisional solution to get the facets API working
# Everything needs to be transfered to PostgreSQL
def populate_facets(
    search: sa.orm.Query, collections: stac_fastapi.types.stac.Collections
) -> CollectionsWithStats:
    """Populate the collections with the search stats about facets."""
    results = search.all()
    all_kws = set(list(itertools.chain(*[r.keywords for r in results])))
    kw_stats = {}
    for kw in all_kws:
        category, keyword = [x.strip() for x in kw.split(":")]
        kw_stats.setdefault(category, []).append(keyword)

    collections["search"] = {
        "kw": [
            # FIXME: let's don't waste time to get the real count in this temporary solution
            {"category": cat, "groups": [{kw: {"count": None}} for kw in kws]}
            for cat, kws in kw_stats.items()
        ]
    }
    return collections
