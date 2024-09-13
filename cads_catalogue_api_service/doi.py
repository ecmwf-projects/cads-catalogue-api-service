"""DOI compatibility routes for CADS."""

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
import structlog

from . import client, dependencies

logger = structlog.getLogger(__name__)

router = fastapi.APIRouter(
    prefix="/doi",
    tags=["doi"],
    responses={fastapi.status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


def query_collection(
    session: sa.orm.Session,
    doi: str,
    request: fastapi.Request,
) -> stac_fastapi.types.stac.Collection:
    """Load a STAC collection from database."""
    return client.collection_serializer(
        session.query(cads_catalogue.database.Resource)
        .filter(cads_catalogue.database.Resource.doi == doi)
        .one(),
        session=session,
        request=request,
    )


@router.get("/{doi_prefix}/{doi_suffix}")
def redirect_by_doi(
    doi_prefix: str,
    doi_suffix: str,
    request: fastapi.Request,
    session=fastapi.Depends(dependencies.get_session),
):
    """Permalink service to redirect to dataset page by querying using DOI.

    Required for keeping DOI compatibility from the old CDS.
    """
    doi = f"{doi_prefix}/{doi_suffix}"
    try:
        collection = query_collection(session, doi, request)
    except sa.orm.exc.NoResultFound as exc:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        ) from exc
    except sa.orm.exc.MultipleResultsFound as exc:
        logger.error("Search by DOI lead to multiple results", doi=doi)
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while searching for this DOI",
        ) from exc

    return fastapi.responses.RedirectResponse(
        url=request.url_for("Get Collection", collection_id=collection["id"]),
        status_code=fastapi.status.HTTP_301_MOVED_PERMANENTLY,
    )
