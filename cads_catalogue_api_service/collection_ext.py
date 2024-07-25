"""Additional collections endpoint (outside STAC)."""

# Copyright 2024, European Union.
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
# mypy: ignore-errors

import cads_catalogue
import fastapi
import sqlalchemy as sa
import stac_fastapi.types
import stac_fastapi.types.core

from cads_catalogue_api_service.client import collection_serializer

from . import dependencies

router = fastapi.APIRouter(
    prefix="",
    responses={fastapi.status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


def query_collection(
    session: sa.orm.Session,
    collection_id: str,
    request: fastapi.Request,
) -> stac_fastapi.types.stac.Collection:
    """Load a STAC collection from database."""
    return collection_serializer(
        session.query(cads_catalogue.database.Resource)
        .filter(cads_catalogue.database.Resource.resource_uid == collection_id)
        .one(),
        session=session,
        request=request,
    )


@router.get(
    "/collections/{collection_id}/form.json",
)
def form_redirect(
    collection_id: str,
    request: fastapi.Request,
    session=fastapi.Depends(dependencies.get_session),
):
    """Redirect to form.json (if defined)."""
    collection = query_collection(session, collection_id, request)
    if "links" in collection and collection["links"]:
        for link in collection["links"]:
            if link["rel"] == "form":
                return fastapi.responses.RedirectResponse(url=link["href"])
    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_404_NOT_FOUND,
        detail=f"Collection {collection_id} has no form definition",
    )


@router.get(
    "/collections/{collection_id}/constraints.json",
)
def constraints_redirect(
    collection_id: str,
    request: fastapi.Request,
    session=fastapi.Depends(dependencies.get_session),
):
    """Redirect to constraints.json (if defined)."""
    collection = query_collection(session, collection_id, request)
    if "links" in collection and collection["links"]:
        for link in collection["links"]:
            if link["rel"] == "constraints":
                return fastapi.responses.RedirectResponse(url=link["href"])
    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_404_NOT_FOUND,
        detail=f"Collection {collection_id} has no constraints definition",
    )
