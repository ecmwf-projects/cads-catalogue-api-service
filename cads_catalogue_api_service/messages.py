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

import fastapi
import sqlalchemy as sa
import random

from . import dependencies, models

router = fastapi.APIRouter(
    prefix="/collections/{collection_id}/messages",
    tags=["messages"],
    responses={fastapi.status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


def query_messages(
    session_maker: sa.orm.Session
) -> list[object]:
    """Query messages."""
    results = [
        {
            "id": "xxx-yyy-zzzz.md",
            "date": "2023-01-20T08:05:54Z",
            "summary": "Found an issue on this dataset",
            "url": "http://object-storage/…/xxx.md",
            "severity": "warn"
        },
        {
            "id": "yyy-zzz-uuuu.md",
            "date": "2023-01-20T11:15:54Z",
            "summary": "Changed something on this other dataset",
            "url": "http://object-storage/…/yyy.md",
            "severity": "info"
        }
        
    ]
    return results


def query_changelogs(
    session_maker: sa.orm.Session
) -> list[object]:
    """Query changelogs."""
    results = []
    severity = ["warn","info","critical"]
    for i in range(10):
        results.append(
        {
            "id": f"{i}-yyy-zzzz.md",
            "date": f"2023-01-{i}T08:05:54Z",
            "summary": "Found a log on this dataset",
            "url": f"http://object-storage/…/{i}.md",
            "severity": random.choice(severity),
            "archived":True,
        })
    return results


@router.get("", response_model=models.Messages)
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
            )
            for message in results
        ]
    )


@router.get("/changelog", response_model=models.Changelogs)
async def list_changelogs(
    session_maker=fastapi.Depends(dependencies.get_session),
) -> models.Changelogs:
    """Endpoint to get all changelogs."""
    results = query_changelogs(session_maker)
    return models.Changelogs(
        changelogs=[
            models.Changelog(
                id=changelog["id"],
                date=changelog["date"],
                summary=changelog["summary"],
                url=changelog["url"],
                severity=changelog["severity"],
                archived=changelog["archived"],
            )
            for changelog in results
        ]
    )
