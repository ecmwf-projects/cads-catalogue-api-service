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
    page: int = fastapi.Query(default=0, ge=0),
    limit: int = fastapi.Query(default=config.MAX_LIMIT, ge=1, le=config.MAX_LIMIT),
    search_stats: bool = fastapi.Query(default=True),
) -> dict[str, Any]:
    """Filter datasets based on search parameters."""
    return client.cads_client.all_datasets(
        request=request,
        q=q,
        kw=kw,
        sortby=sortby,
        page=page,
        limit=limit,
        route_name="Datasets Search",
        search_stats=search_stats,
    )


@attr.s
class DatasetsSearchExtension(stac_fastapi.types.extension.ApiExtension):
    """Datasets filter extension.

    This filter extension adds a new /datasets endpoint
    (can't be "/search" because STAC reserves it for search on items).
    """

    conformance_classes: list[str] = attr.ib(
        default=[
            "https://github.com/ecmwf-projects/cads-catalogue-api-service/stac-extentions/datasets-search"
        ]
    )
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


@attr.s
class CADSDatasetExtension(stac_fastapi.types.extension.ApiExtension):
    """Datasets extentions for CADS catalogue."""

    conformance_classes: list[str] = attr.ib(
        default=[
            "https://github.com/ecmwf-projects/cads-catalogue-api-service/stac-extentions/cads-dataset"
        ]
    )
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
        pass
