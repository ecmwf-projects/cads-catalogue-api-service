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

import random

import fastapi
import sqlalchemy as sa

from . import dependencies, models

router = fastapi.APIRouter(
    prefix="",
    tags=["messages"],
    responses={fastapi.status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


def query_messages(session_maker: sa.orm.Session) -> list[object]:
    """Query messages."""
    results = [
        {
            "id": "xxx-yyy-zzzz.md",
            "date": "2023-01-20T08:05:54Z",
            "summary": "Found an issue on this dataset",
            "url": "http://object-storage/…/xxx.md",
            "severity": "warn",
            "entries": "dataset1",
            "live": True,
        },
        {
            "id": "yyy-zzz-uuuu.md",
            "date": "2023-01-20T11:15:54Z",
            "summary": "Changed something on this other dataset",
            "url": "http://object-storage/…/yyy.md",
            "severity": "info",
            "entries": "dataset2",
            "live": True,
        },
    ]
    return results


def query_changelog_list(session_maker: sa.orm.Session) -> list[object]:
    """Query changelog list."""
    results = []
    severity = ["warn", "info", "critical"]
    for i in range(10):
        results.append(
            {
                "id": f"{i}-yyy-zzzz.md",
                "date": f"2023-01-{i}T08:05:54Z",
                "summary": "Found a log on this dataset",
                "url": f"http://object-storage/…/{i}.md",
                "severity": random.choice(severity),
                "archived": True,
                "entries": "dataset1,dataset2",
                "live": False,
                "status": "fixed",
            }
        )
    return results


@router.get("/collections/{collection_id}/messages", response_model=models.Messages)
async def list_messages_by_id(
    session_maker=fastapi.Depends(dependencies.get_session),
) -> models.Message:
    """Endpoint to get all messages of a specific collection."""
    results = query_messages(session_maker)
    return models.Messages(
        messages=[
            models.Message(
                id=message["id"],
                date=message["date"],
                summary=message["summary"],
                url=message["url"],
                severity=message["severity"],
                entries=message["entries"],
                live=message["live"],
            )
            for message in results
        ]
    )


@router.get(
    "/collections/{collection_id}/messages/changelog",
    response_model=models.ChangelogList,
)
async def list_changelog_by_id(
    session_maker=fastapi.Depends(dependencies.get_session),
) -> models.ChangelogList:
    """Endpoint to get all changelog of a specific collection."""
    results = query_changelog_list(session_maker)
    return models.ChangelogList(
        changelog=[
            models.Changelog(
                id=changelog["id"],
                date=changelog["date"],
                summary=changelog["summary"],
                url=changelog["url"],
                severity=changelog["severity"],
                entries=changelog["entries"],
                live=changelog["live"],
                status=changelog["status"],
            )
            for changelog in results
        ]
    )


@router.get("/messages", response_model=models.Messages)
async def list_messages(
    session_maker=fastapi.Depends(dependencies.get_session),
) -> models.Message:
    """Endpoint to get all messages."""
    results = query_messages(session_maker)
    return models.Messages(
        messages=[
            models.Message(
                id=message["id"],
                date=message["date"],
                summary=message["summary"],
                url=message["url"],
                severity=message["severity"],
                entries=message["entries"],
                live=message["live"],
            )
            for message in results
        ]
    )


@router.get("/messages/changelog", response_model=models.ChangelogList)
async def list_changelog(
    session_maker=fastapi.Depends(dependencies.get_session),
) -> models.ChangelogList:
    """Endpoint to get all changelog."""
    results = query_changelog_list(session_maker)
    return models.ChangelogList(
        changelog=[
            models.Changelog(
                id=changelog["id"],
                date=changelog["date"],
                summary=changelog["summary"],
                url=changelog["url"],
                severity=changelog["severity"],
                entries=changelog["entries"],
                live=changelog["live"],
                status=changelog["status"],
            )
            for changelog in results
        ]
    )
