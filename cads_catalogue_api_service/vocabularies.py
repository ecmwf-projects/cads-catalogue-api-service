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
import sqlalchemy

from . import dependencies, models

router = fastapi.APIRouter(
    prefix="/vocabularies",
    tags=["vocabularies"],
    responses={fastapi.status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


def query_licences(
    session_maker: sqlalchemy.orm.Session,
) -> list[cads_catalogue.database.Licence]:  # pragma: no cover
    """Query licences."""
    with session_maker.context_session() as session:
        # NOTE: possible issue here if the title of a licence change from a revision to another
        results = (
            session.query(
                cads_catalogue.database.Licence.licence_uid,
                cads_catalogue.database.Licence.title,
                sqlalchemy.func.max(cads_catalogue.database.Licence.revision).label(
                    "revision"
                ),
            )
            .group_by(
                cads_catalogue.database.Licence.licence_uid,
                cads_catalogue.database.Licence.title,
            )
            .all()
        )
    return results


@router.get("/licences", response_model=models.Licences)
async def list_licences(
    session_maker=fastapi.Depends(dependencies.get_session),
) -> models.Licences:
    """Endpoint to verify a user's PAT."""
    results = query_licences(session_maker)
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
