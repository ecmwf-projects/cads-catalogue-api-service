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
    session_maker: sa.orm.Session,
    live: bool = True,
    collection_id: str | None = None,
) -> list[cads_catalogue.database.Message]:
    """Query messages."""
    with session_maker.context_session() as session:
        results = session.query(
            cads_catalogue.database.Message.message_id,
            cads_catalogue.database.Message.date,
            cads_catalogue.database.Message.summary,
            cads_catalogue.database.Message.url,
            cads_catalogue.database.Message.severity,
            cads_catalogue.database.Message.content,
            cads_catalogue.database.Message.live,
            cads_catalogue.database.Message.status,
        ).where(cads_catalogue.database.Message.live.is_(live))
        if collection_id:
            results = results.where(
                cads_catalogue.database.Message.entries.contains(collection_id)
            )
        results = results.order_by(sa.desc(cads_catalogue.database.Message.date)).all()
    return results


@router.get("/collections/{collection_id}/messages", response_model=models.Messages)
def list_messages_by_id(
    collection_id: str,
    session_maker=fastapi.Depends(dependencies.get_session),
) -> models.Message:
    """Endpoint to get all messages of a specific collection."""
    results = query_messages(session_maker, True, collection_id)
    return models.Messages(
        messages=[
            models.Message(
                message_id=message.message_id,
                date=message.date,
                summary=message.summary,
                url=message.url,
                severity=message.severity,
                content=message.content,
                live=message.live,
                status=message.status,
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
    session_maker=fastapi.Depends(dependencies.get_session),
) -> models.Changelog:
    """Endpoint to get all changelog of a specific collection."""
    results = query_messages(session_maker, False, collection_id)
    return models.Changelog(
        changelog=[
            models.Message(
                message_id=message.message_id,
                date=message.date,
                summary=message.summary,
                url=message.url,
                severity=message.severity,
                content=message.content,
                live=message.live,
                status=message.status,
            )
            for message in results
        ]
    )


@router.get("/messages", response_model=models.Messages)
def list_messages(
    session_maker=fastapi.Depends(dependencies.get_session),
) -> models.Message:
    """Endpoint to get all messages."""
    results = query_messages(session_maker, True)
    return models.Messages(
        messages=[
            models.Message(
                message_id=message.message_id,
                date=message.date,
                summary=message.summary,
                url=message.url,
                severity=message.severity,
                content=message.content,
                live=message.live,
                status=message.status,
            )
            for message in results
        ]
    )


@router.get("/messages/changelog", response_model=models.Changelog)
def list_changelog(
    session_maker=fastapi.Depends(dependencies.get_session),
) -> models.Changelog:
    """Endpoint to get all changelog."""
    results = query_messages(session_maker, False)
    return models.Changelog(
        changelog=[
            models.Message(
                message_id=message.message_id,
                date=message.date,
                summary=message.summary,
                url=message.url,
                severity=message.severity,
                content=message.content,
                live=message.live,
                status=message.status,
            )
            for message in results
        ]
    )
