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

import enum
import urllib

import cads_catalogue
import fastapi
import sqlalchemy as sa

from . import config, dependencies, models


class LicenceScopeCriterion(str, enum.Enum):
    all: str = "all"
    dataset: str = "dataset"
    portal: str = "portal"


router = fastapi.APIRouter(
    prefix="/vocabularies",
    tags=["vocabularies"],
    responses={fastapi.status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


def query_licences(
    session: sa.orm.Session,
    scope: LicenceScopeCriterion,
) -> list[cads_catalogue.database.Licence]:
    """Query licences."""
    # NOTE: possible issue here if the title of a licence change from a revision to another
    query = session.query(
        cads_catalogue.database.Licence.licence_uid,
        cads_catalogue.database.Licence.title,
        cads_catalogue.database.Licence.md_filename,
        cads_catalogue.database.Licence.download_filename,
        sa.func.max(cads_catalogue.database.Licence.revision).label("revision"),
        cads_catalogue.database.Licence.scope,
    )
    if scope and scope != LicenceScopeCriterion.all:
        query = query.filter(cads_catalogue.database.Licence.scope == scope)
    results = (
        query.group_by(
            cads_catalogue.database.Licence.licence_uid,
            cads_catalogue.database.Licence.title,
            cads_catalogue.database.Licence.md_filename,
            cads_catalogue.database.Licence.download_filename,
            cads_catalogue.database.Licence.scope,
        )
        .order_by(cads_catalogue.database.Licence.title)
        .all()
    )
    return results


def query_licence(
    session: sa.orm.Session,
    licence_uid: str,
) -> list[cads_catalogue.database.Licence]:
    """Query a single licence data."""
    query = session.query(
        cads_catalogue.database.Licence.licence_uid,
        cads_catalogue.database.Licence.title,
        cads_catalogue.database.Licence.md_filename,
        cads_catalogue.database.Licence.download_filename,
        sa.func.max(cads_catalogue.database.Licence.revision).label("revision"),
        cads_catalogue.database.Licence.scope,
    )
    query = query.filter(cads_catalogue.database.Licence.licence_uid == licence_uid)
    results = (
        query.group_by(
            cads_catalogue.database.Licence.licence_uid,
            cads_catalogue.database.Licence.title,
            cads_catalogue.database.Licence.md_filename,
            cads_catalogue.database.Licence.download_filename,
            cads_catalogue.database.Licence.scope,
        )
        .order_by(cads_catalogue.database.Licence.title)
        .one()
    )
    return results


def query_keywords(
    session: sa.orm.Session,
) -> list[str]:
    """Query keywords."""
    results = (
        session.query(cads_catalogue.database.Keyword)
        .order_by(cads_catalogue.database.Keyword.keyword_name)
        .all()
    )
    return results


@router.get("/licences", response_model=models.Licences)
async def list_licences(
    session=fastapi.Depends(dependencies.get_session),
    scope: LicenceScopeCriterion = fastapi.Query(default=LicenceScopeCriterion.all),
) -> models.Licences:
    """Endpoint to get all registered licences."""
    results = query_licences(session, scope)
    return models.Licences(
        licences=[
            models.Licence(
                id=licence.licence_uid,
                label=licence.title,
                revision=licence.revision,
                contents_url=urllib.parse.urljoin(
                    config.settings.document_storage_url, licence.md_filename
                ),
                attachment_url=urllib.parse.urljoin(
                    config.settings.document_storage_url, licence.download_filename
                ),
                scope=licence.scope,
            )
            for licence in results
        ]
    )


@router.get("/licences/{licence_uid}", response_model=models.Licence)
async def list_licence(
    session=fastapi.Depends(dependencies.get_session),
    licence_uid: str = fastapi.Path(..., title="Licence UID"),
) -> models.Licences:
    """Endpoint to get all registered licences."""
    licence = query_licence(session, licence_uid)
    return models.Licence(
        id=licence.licence_uid,
        label=licence.title,
        revision=licence.revision,
        contents_url=urllib.parse.urljoin(
            config.settings.document_storage_url, licence.md_filename
        ),
        attachment_url=urllib.parse.urljoin(
            config.settings.document_storage_url, licence.download_filename
        ),
        scope=licence.scope,
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
                id=keyword.keyword_name,
                label=keyword.keyword_name,
            )
            for keyword in results
        ]
    )
