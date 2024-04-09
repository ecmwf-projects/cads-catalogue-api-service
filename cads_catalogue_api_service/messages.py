"""Messages module."""

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
    prefix="",
    tags=["messages"],
    responses={fastapi.status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


def query_messages(
    session: sa.orm.Session,
    live: bool = True,
    is_global: bool = True,
    collection_id: str | None = None,
    portals: list[str] | None = None,
) -> list[cads_catalogue.database.Message]:
    """Query messages."""
    results = (
        session.query(
            cads_catalogue.database.Message.message_uid,
            cads_catalogue.database.Message.date,
            cads_catalogue.database.Message.summary,
            cads_catalogue.database.Message.url,
            cads_catalogue.database.Message.severity,
            cads_catalogue.database.Message.content,
            cads_catalogue.database.Message.live,
        )
        .join(
            cads_catalogue.database.ResourceMessage,
            isouter=True,
        )
        # FIXEME: this can be slow. Please do not load the full dataset.
        .join(
            cads_catalogue.database.Resource,
            full=True,
        )
        .where(
            cads_catalogue.database.Message.live.is_(live),
            cads_catalogue.database.Message.is_global.is_(is_global),
        )
    )
    if portals and is_global:
        results = results.where(
            sa.or_(
                cads_catalogue.database.Message.portal.in_(portals),
                cads_catalogue.database.Message.portal.is_(None),
            ),
        )
    if collection_id:
        results = results.where(
            cads_catalogue.database.Resource.resource_uid == collection_id
        )
    results = results.order_by(sa.desc(cads_catalogue.database.Message.date)).all()  # type: ignore
    return results  # type: ignore


@router.get("/collections/{collection_id}/messages", response_model=models.Messages)
def list_messages_by_id(
    collection_id: str,
    session=fastapi.Depends(dependencies.get_session),
) -> models.Messages:
    """Endpoint to get all messages of a specific collection."""
    results = query_messages(
        session=session,
        live=True,
        is_global=False,
        collection_id=collection_id,
    )
    return models.Messages(
        messages=[
            models.Message(
                id=message.message_uid,
                date=message.date,
                summary=message.summary,
                url=message.url,
                severity=message.severity,
                content=message.content,
                live=message.live,
            )
            for message in results
        ]
    )


@router.get(
    "/collections/{collection_id}/messages/changelog",
    response_model=models.Changelog,
)
def list_changelog_by_id(
    collection_id: str,
    session=fastapi.Depends(dependencies.get_session),
) -> models.Changelog:
    """Endpoint to get all changelog of a specific collection."""
    results = query_messages(
        session=session, live=False, is_global=False, collection_id=collection_id
    )
    return models.Changelog(
        changelog=[
            models.Message(
                id=message.message_uid,
                date=message.date,
                summary=message.summary,
                url=message.url,
                severity=message.severity,
                content=message.content,
                live=message.live,
            )
            for message in results
        ]
    )


@router.get("/messages", response_model=models.Messages)
def list_messages(
    session=fastapi.Depends(dependencies.get_session),
    portals: list[str] | None = fastapi.Depends(dependencies.get_portals),
) -> models.Messages:
    """Endpoint to get all messages."""
    results = query_messages(
        session=session, live=True, is_global=True, portals=portals
    )
    return models.Messages(
        messages=[
            models.Message(
                id=message.message_uid,
                date=message.date,
                summary=message.summary,
                url=message.url,
                severity=message.severity,
                content=message.content,
                live=message.live,
            )
            for message in results
        ]
    )


@router.get("/messages/changelog", response_model=models.Changelog)
def list_changelog(
    session=fastapi.Depends(dependencies.get_session),
    portals: list[str] | None = fastapi.Depends(dependencies.get_portals),
) -> models.Changelog:
    """Endpoint to get all changelog."""
    results = query_messages(
        session=session, live=False, is_global=True, portals=portals
    )
    return models.Changelog(
        changelog=[
            models.Message(
                id=message.message_uid,
                date=message.date,
                summary=message.summary,
                url=message.url,
                severity=message.severity,
                content=message.content,
                live=message.live,
            )
            for message in results
        ]
    )
