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

import attr
import fastapi
import pydantic
import stac_fastapi.types.extension
import stac_fastapi.types.stac

from . import client, config, search_utils


class CatalogueSortCriterion(str, enum.Enum):
    """Sorting criteria for datasets search."""

    publication_desc = "publication"
    relevance_desc = "relevance"
    update_desc = "update"
    title_asc = "title"
    id_asc = "id"


class ContentSortCriterion(str, enum.Enum):
    """Sorting criteria for contents search."""

    title_asc = "title"
    publication_desc = "publication"
    update_desc = "update"


def datasets_search(
    request: fastapi.Request,
    q: str = fastapi.Query(default=None, description="Full-text search query"),
    kw: list[str] | None = fastapi.Query(
        default=[], description="Filter by keyword(s)"
    ),
    idx: list[str] | None = fastapi.Query(
        default=[], description="Filter by dataset IDs"
    ),
    sortby: CatalogueSortCriterion = fastapi.Query(
        default=CatalogueSortCriterion.update_desc
    ),
    page: int = fastapi.Query(default=0, ge=0),
    limit: int = fastapi.Query(
        default=config.settings.catalogue_page_size,
        ge=1,
        le=config.settings.catalogue_max_page_size,
    ),
    search_stats: bool = fastapi.Query(
        default=True,
        description="Include additional search statistics in results (like: faceted data)",
    ),
) -> stac_fastapi.types.stac.Collections | search_utils.CollectionsWithStats:
    """Filter datasets based on search parameters."""
    return client.cads_client.all_datasets(
        request=request,
        q=q,
        kw=kw,
        idx=idx,
        sortby=sortby,
        page=page,
        limit=limit,
        route_name="Datasets Search",
        search_stats=search_stats,
    )


class FormData(pydantic.BaseModel):
    """Search datasets valid payload."""

    q: str = ""
    kw: list[str] | None = []
    idx: list[str] | None = []
    sortby: CatalogueSortCriterion = CatalogueSortCriterion.update_desc
    page: int = 0
    limit: int = config.settings.catalogue_page_size
    search_stats: bool = True


def datasets_search_post(
    request: fastapi.Request, data: FormData
) -> stac_fastapi.types.stac.Collections | search_utils.CollectionsWithStats:
    """Filter datasets based on search parameters."""
    return datasets_search(
        request=request,
        q=data.q,
        kw=data.kw,
        idx=data.idx,
        sortby=data.sortby,
        page=data.page,
        limit=data.limit,
        search_stats=data.search_stats,
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
            endpoint=datasets_search,
        )
        self.router.add_api_route(
            name="Datasets Search",
            path="/datasets",
            methods=["POST"],
            endpoint=datasets_search_post,
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
