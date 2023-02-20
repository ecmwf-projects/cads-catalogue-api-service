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
        results = session.query(models.Changelog).where(
            cads_catalogue.database.Message.live.is_(live)
        )
        if collection_id:
            results = results.where(
                cads_catalogue.database.Message.entries.contains(collection_id)
            )
        results = results.order_by(cads_catalogue.database.Message.date).all()
    return results


@router.get("/collections/{collection_id}/messages", response_model=models.Messages)
async def list_messages_by_id(
    collection_id: str,
    session_maker=fastapi.Depends(dependencies.get_session),
) -> models.Message:
    """Endpoint to get all messages of a specific collection."""
    results = query_messages(session_maker, live=True, collection_id=collection_id)
    return models.Messages(
        messages=[
            models.Message(
                message_id=message.message_id,
                date=message.date,
                summary=message.summary,
                url=message.url,
                severity=message.severity,
                entries=message.entries,
                live=message.live,
            )
            for message in results
        ]
    )


@router.get(
    "/collections/{collection_id}/messages/changelog",
    response_model=models.ChangelogList,
)
async def list_changelog_by_id(
    collection_id: str,
    session_maker=fastapi.Depends(dependencies.get_session),
) -> models.ChangelogList:
    """Endpoint to get all changelog of a specific collection."""
    results = query_messages(session_maker, live=False, collection_id=collection_id)
    return models.ChangelogList(
        changelog=[
            models.Changelog(
                message_id=changelog.message_id,
                date=changelog.date,
                summary=changelog.summary,
                url=changelog.url,
                severity=changelog.severity,
                entries=changelog.entries,
                live=changelog.live,
                status=changelog.status,
            )
            for changelog in results
        ]
    )


@router.get("/messages", response_model=models.Messages)
async def list_messages(
    session_maker=fastapi.Depends(dependencies.get_session),
) -> models.Message:
    """Endpoint to get all messages."""
    results = query_messages(session_maker, live=True)
    return models.Messages(
        messages=[
            models.Message(
                message_id=message.message_id,
                date=message.date,
                summary=message.summary,
                url=message.url,
                severity=message.severity,
                entries=message.entries,
                live=message.live,
            )
            for message in results
        ]
    )


@router.get("/messages/changelog", response_model=models.ChangelogList)
async def list_changelog(
    session_maker=fastapi.Depends(dependencies.get_session),
) -> models.ChangelogList:
    """Endpoint to get all changelog."""
    results = query_messages(session_maker, live=False)
    return models.ChangelogList(
        changelog=[
            models.Changelog(
                message_id=changelog.message_id,
                date=changelog.date,
                summary=changelog.summary,
                url=changelog.url,
                severity=changelog.severity,
                entries=changelog.entries,
                live=changelog.live,
                status=changelog.status,
            )
            for changelog in results
        ]
    )
