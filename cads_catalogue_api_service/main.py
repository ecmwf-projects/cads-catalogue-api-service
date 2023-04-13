"""Main STAC based API module.

This largely depends on stac_fastapi to generate the RESTful API.
"""

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

from contextlib import asynccontextmanager
from typing import Any

import cads_common.logging
import fastapi
import fastapi.middleware.cors
import fastapi.openapi
import fastapi.responses
import stac_fastapi.api.app
import stac_fastapi.extensions.core
import stac_fastapi.types
import stac_fastapi.types.conformance
import stac_fastapi.types.links
import starlette
from brotli_asgi import BrotliMiddleware
from starlette_exporter import PrometheusMiddleware, handle_metrics

from . import (
    client,
    config,
    exceptions,
    extensions,
    messages,
    middlewares,
    vocabularies,
)


@asynccontextmanager
async def lifespan(application: fastapi.FastAPI):
    cads_common.logging.config_logging()
    yield


extensions = [
    # This extenstion is required, seems for a bad implementation
    stac_fastapi.extensions.core.TokenPaginationExtension(),
    extensions.DatasetsSearchExtension(),
]

api = stac_fastapi.api.app.StacApi(
    settings=config.dbsettings,
    extensions=extensions,
    client=client.cads_client,
    middlewares=[
        BrotliMiddleware,
        PrometheusMiddleware,
        stac_fastapi.api.middleware.CORSMiddleware,
        middlewares.CacheControlMiddleware,
        middlewares.LoggerInitializationMiddleware,
    ],
)

app = api.app
app.router.lifespan_context = lifespan
app.add_route("/metrics", handle_metrics)
app.include_router(vocabularies.router)
app.include_router(messages.router)


def catalogue_openapi() -> dict[str, Any]:
    """OpenAPI, but with not implemented paths removed."""
    openapi_schema = fastapi.openapi.utils.get_openapi(
        title="CADS Catalogue", version=api.api_version, routes=api.app.routes
    )

    del openapi_schema["paths"]["/collections/{collection_id}/items"]
    del openapi_schema["paths"]["/collections/{collection_id}/items/{item_id}"]
    del openapi_schema["paths"]["/search"]

    openapi_schema["servers"] = [{"url": "/api/catalogue/v1"}]

    return openapi_schema


app.openapi = catalogue_openapi


@app.exception_handler(exceptions.FeatureNotImplemented)
async def feature_not_implemented_handler(
    request: fastapi.Request, exc: exceptions.FeatureNotImplemented
) -> fastapi.responses.JSONResponse:
    """Catch FeatureNotImplemented exceptions to properly trigger an HTTP 501."""
    return exceptions.generate_exception_response(title=exc.message, status_code=501)


@app.exception_handler(starlette.exceptions.HTTPException)
async def http_exception_handler(
    request: fastapi.Request, exc: starlette.exceptions.HTTPException
):
    return exceptions.generate_exception_response(
        title=exc.detail, status_code=exc.status_code
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: fastapi.Request, exc: Exception):
    return exceptions.generate_exception_response(
        title="internal server error",
        status_code=starlette.status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
