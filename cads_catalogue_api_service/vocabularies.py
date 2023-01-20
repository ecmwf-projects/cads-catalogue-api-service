"""Vocabularies module."""

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

import cads_catalogue
import fastapi
import sqlalchemy as sa

from . import dependencies, models

router = fastapi.APIRouter(
    prefix="/vocabularies",
    tags=["vocabularies"],
    responses={fastapi.status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


def query_licences(
    session: sa.orm.Session,
) -> list[cads_catalogue.database.Licence]:
    """Query licences."""
    # NOTE: possible issue here if the title of a licence change from a revision to another
    results = (
        session.query(
            cads_catalogue.database.Licence.licence_uid,
            cads_catalogue.database.Licence.title,
            sa.func.max(cads_catalogue.database.Licence.revision).label("revision"),
        )
        .group_by(
            cads_catalogue.database.Licence.licence_uid,
            cads_catalogue.database.Licence.title,
        )
        .order_by(cads_catalogue.database.Licence.title)
        .all()
    )
    return results


def query_keywords(
    session: sa.orm.Session,
) -> list[str]:
    """Query keywords."""
    results = (
        session.query(sa.func.unnest(cads_catalogue.database.Resource.keywords))
        .distinct()
        .order_by(sa.func.unnest(cads_catalogue.database.Resource.keywords))
        .all()
    )
    return [col[0] for col in results]


@router.get("/licences", response_model=models.Licences)
async def list_licences(
    session=fastapi.Depends(dependencies.get_session),
) -> models.Licences:
    """Endpoint to get all registered licences."""
    results = query_licences(session)
    return models.Licences(
        licences=[
            models.Licence(
                id=licence.licence_uid,
                label=licence.title,
                revision=licence.revision,
            )
            for licence in results
        ]
    )


@router.get("/keywords", response_model=models.Keywords)
async def list_keywords(
    session=fastapi.Depends(dependencies.get_session),
) -> models.Keywords:
    """Endpoint to get all available keywords."""
    results = query_keywords(session)
    return models.Keywords(
        keywords=[
            models.Keyword(
                id=keyword,
                label=keyword,
            )
            for keyword in results
        ]
    )
