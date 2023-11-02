"""Custom STAC extentions."""

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

import enum
from typing import Any

import attr
import fastapi
import stac_fastapi.api
import stac_fastapi.types.extension

from . import client, config

CONFORMANCE_CLASS = "https://api.cads.copernicus.eu/v1.0.0-rc.1/datasets-search#filter"


class CatalogueSortCriterion(str, enum.Enum):
    relevance_desc: str = "relevance"
    update_desc: str = "update"
    title_asc: str = "title"
    id_asc: str = "id"


def datasets_search(
    request: fastapi.Request,
    q: str = fastapi.Query(default=None, description="Full-text search query"),
    kw: list[str] | None = fastapi.Query(default=[]),
    sortby: CatalogueSortCriterion = fastapi.Query(
        default=CatalogueSortCriterion.update_desc
    ),
    # FIXME: remove this deprecated parameter
    sorting: CatalogueSortCriterion = fastapi.Query(
        default=None,
        deprecated=True,
        description="Deprecated, use sortby instead.",
    ),
    cursor: str = fastapi.Query(default=None, include_in_schema=False),
    limit: int = fastapi.Query(default=config.MAX_LIMIT, ge=1, le=config.MAX_LIMIT),
    back: bool = fastapi.Query(default=False, include_in_schema=False),
    search_stats: bool = True,
) -> dict[str, Any]:
    """Filter datasets based on search parameters."""
    return client.cads_client.all_datasets(
        request=request,
        q=q,
        kw=kw,
        sortby=sorting or sortby,
        cursor=cursor,
        limit=limit,
        back=back,
        route_name="Datasets Search",
        search_stats=search_stats,
    )


@attr.s
class DatasetsSearchExtension(stac_fastapi.types.extension.ApiExtension):
    """Datasets filter extension.

    This filter extension adds a new /datasets endpoint
    (can't be "/search" because STAC reserves it for search on items).
    """

    conformance_classes: list[str] = attr.ib(default=[CONFORMANCE_CLASS])
    router: fastapi.APIRouter = attr.ib(factory=fastapi.APIRouter)
    # response_class: Type[starlette.responses.Response] = attr.ib(
    #     default=starlette.responses.JSONResponse
    # )

    def register(self, app: fastapi.FastAPI) -> None:
        """Register the extension with a FastAPI application.

        Args
        ----
            app: target FastAPI application.

        Returns
        -------
            None
        """
        # FIXME: not here on this version on stac_fastapi
        # self.router.prefix = app.state.router_prefix
        self.router.add_api_route(
            name="Datasets Search",
            path="/datasets",
            methods=["GET"],
            # endpoint=stac_fastapi.api.routes.create_async_endpoint(
            #     datasets_search,
            #     stac_fastapi.api.models.EmptyRequest,
            #     self.response_class,
            # ),
            endpoint=datasets_search,
        )
        app.include_router(self.router, tags=["Datasets Search Extension"])
