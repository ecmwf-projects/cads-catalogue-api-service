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

import logging
from typing import Any

import fastapi
import fastapi.openapi
import fastapi.responses
import stac_fastapi.api.app
import stac_fastapi.extensions.core
import stac_fastapi.types
import stac_fastapi.types.conformance
import stac_fastapi.types.links

from . import client, config, exceptions, extensions

logger = logging.getLogger(__name__)

extensions = [
    # This extenstion is required, seems for a bad implementation
    stac_fastapi.extensions.core.TokenPaginationExtension(),
    extensions.DatasetsSearchExtension(),
]

api = stac_fastapi.api.app.StacApi(
    settings=config.dbsettings,
    extensions=extensions,
    client=client.cads_client,
)

app = api.app


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


@app.exception_handler(exceptions.FeatureNotImplemented)  # type: ignore
async def unicorn_exception_handler(
    request: fastapi.Request, exc: exceptions.FeatureNotImplemented
) -> fastapi.responses.JSONResponse:
    """Catch FeatureNotImplemented exceptions to properly trigger an HTTP 501."""
    return fastapi.responses.JSONResponse(
        status_code=501,
        content={"message": exc.message},
    )
