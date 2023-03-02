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

from typing import Any

import cads_catalogue
import fastapi
import fastapi.testclient

import cads_catalogue_api_service
from cads_catalogue_api_service.main import app

client = fastapi.testclient.TestClient(app)


class Message:
    def __init__(
        self,
        message_id: str,
        date: str,
        summary: str,
        url: str,
        severity: str,
        content: str,
        live: bool,
        status: str,
    ):
        self.message_id = message_id
        self.date = date
        self.summary = summary
        self.url = url
        self.severity = severity
        self.content = content
        self.live = live
        self.status = status


def static_messages_query(
    session: Any, live: bool = True, collection_id: str | None = None
) -> list[cads_catalogue.database.Message]:
    return [
        Message(
            message_id="0-yyy-zzzz.md",
            date="2023-01-01T08:05:54+00:00",
            summary="Found a log on this dataset",
            url="http://object-storage/…/0.md",
            severity="info",
            content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
            live=True,
            status="ongoing",
        ),
        Message(
            message_id="1-yyy-zzzz.md",
            date="2023-01-02T08:05:54+00:00",
            summary="Found a log on this dataset",
            url="http://object-storage/…/1.md",
            severity="warning",
            content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
            live=True,
            status="ongoing",
        ),
    ]


def static_changelog_query(
    session: Any, live: bool = False, collection_id: str | None = None
) -> list[cads_catalogue.database.Message]:
    return [
        Message(
            message_id="0-yyy-zzzz.md",
            date="2023-01-01T08:05:54+00:00",
            summary="Found a log on this dataset",
            url="http://object-storage/…/0.md",
            severity="info",
            content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
            live=False,
            status="ongoing",
        ),
        Message(
            message_id="1-yyy-zzzz.md",
            date="2023-01-02T08:05:54+00:00",
            summary="Found a log on this dataset",
            url="http://object-storage/…/1.md",
            severity="warning",
            content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
            live=False,
            status="ongoing",
        ),
        Message(
            message_id="2-yyy-zzzz.md",
            date="2023-01-03T08:05:54+00:00",
            summary="Found a log on this dataset",
            url="http://object-storage/…/2.md",
            severity="warning",
            content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
            live=False,
            status="ongoing",
        ),
        Message(
            message_id="3-yyy-zzzz.md",
            date="2023-01-04T08:05:54+00:00",
            summary="Found a log on this dataset",
            url="http://object-storage/…/3.md",
            severity="warning",
            content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
            live=False,
            status="ongoing",
        ),
        Message(
            message_id="4-yyy-zzzz.md",
            date="2023-01-05T08:05:54+00:00",
            summary="Found a log on this dataset",
            url="http://object-storage/…/4.md",
            severity="warning",
            content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
            live=False,
            status="ongoing",
        ),
        Message(
            message_id="5-yyy-zzzz.md",
            date="2023-01-05T08:05:54+00:00",
            summary="Found a log on this dataset",
            url="http://object-storage/…/5.md",
            severity="warning",
            content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
            live=False,
            status="ongoing",
        ),
        Message(
            message_id="6-yyy-zzzz.md",
            date="2023-01-06T08:05:54+00:00",
            summary="Found a log on this dataset",
            url="http://object-storage/…/6.md",
            severity="warning",
            content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
            live=False,
            status="ongoing",
        ),
    ]


def get_session() -> None:
    """Mock session generation."""
    return None


app.dependency_overrides[
    cads_catalogue_api_service.dependencies.get_session
] = get_session


def test_messages(monkeypatch) -> None:
    monkeypatch.setattr(
        "cads_catalogue_api_service.messages.query_messages",
        static_messages_query,
    )
    """Test list of messages."""
    response = client.get(
        "/collections/my-dataset/messages",
    )

    assert response.status_code == 200
    assert response.json() == {
        "messages": [
            {
                "message_id": "0-yyy-zzzz.md",
                "date": "2023-01-01T08:05:54+00:00",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/0.md",
                "severity": "info",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
                "live": True,
                "status": "ongoing",
            },
            {
                "message_id": "1-yyy-zzzz.md",
                "date": "2023-01-02T08:05:54+00:00",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/1.md",
                "severity": "warning",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
                "live": True,
                "status": "ongoing",
            },
        ],
    }


def test_messages_all(monkeypatch) -> None:
    monkeypatch.setattr(
        "cads_catalogue_api_service.messages.query_messages",
        static_messages_query,
    )
    """Test list of messages."""
    response = client.get(
        "/messages",
    )

    assert response.status_code == 200
    assert response.json() == {
        "messages": [
            {
                "message_id": "0-yyy-zzzz.md",
                "date": "2023-01-01T08:05:54+00:00",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/0.md",
                "severity": "info",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
                "live": True,
                "status": "ongoing",
            },
            {
                "message_id": "1-yyy-zzzz.md",
                "date": "2023-01-02T08:05:54+00:00",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/1.md",
                "severity": "warning",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
                "live": True,
                "status": "ongoing",
            },
        ],
    }


def test_changelog(monkeypatch) -> None:
    monkeypatch.setattr(
        "cads_catalogue_api_service.messages.query_messages",
        static_changelog_query,
    )
    """Test list of changelog."""
    response = client.get(
        "/collections/my-dataset/messages/changelog",
    )

    assert response.status_code == 200
    assert response.json() == {
        "changelog": [
            {
                "message_id": "0-yyy-zzzz.md",
                "date": "2023-01-01T08:05:54+00:00",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/0.md",
                "severity": "info",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
                "live": False,
                "status": "ongoing",
            },
            {
                "message_id": "1-yyy-zzzz.md",
                "date": "2023-01-02T08:05:54+00:00",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/1.md",
                "severity": "warning",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
                "live": False,
                "status": "ongoing",
            },
            {
                "message_id": "2-yyy-zzzz.md",
                "date": "2023-01-03T08:05:54+00:00",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/2.md",
                "severity": "warning",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
                "live": False,
                "status": "ongoing",
            },
            {
                "message_id": "3-yyy-zzzz.md",
                "date": "2023-01-04T08:05:54+00:00",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/3.md",
                "severity": "warning",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
                "live": False,
                "status": "ongoing",
            },
            {
                "message_id": "4-yyy-zzzz.md",
                "date": "2023-01-05T08:05:54+00:00",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/4.md",
                "severity": "warning",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
                "live": False,
                "status": "ongoing",
            },
            {
                "message_id": "5-yyy-zzzz.md",
                "date": "2023-01-05T08:05:54+00:00",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/5.md",
                "severity": "warning",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
                "live": False,
                "status": "ongoing",
            },
            {
                "message_id": "6-yyy-zzzz.md",
                "date": "2023-01-06T08:05:54+00:00",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/6.md",
                "severity": "warning",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
                "live": False,
                "status": "ongoing",
            },
        ],
    }


def test_changelog_all(monkeypatch) -> None:
    monkeypatch.setattr(
        "cads_catalogue_api_service.messages.query_messages",
        static_changelog_query,
    )
    """Test list of all changelog."""
    response = client.get(
        "/messages/changelog",
    )

    assert response.status_code == 200
    assert response.json() == {
        "changelog": [
            {
                "message_id": "0-yyy-zzzz.md",
                "date": "2023-01-01T08:05:54+00:00",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/0.md",
                "severity": "info",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
                "live": False,
                "status": "ongoing",
            },
            {
                "message_id": "1-yyy-zzzz.md",
                "date": "2023-01-02T08:05:54+00:00",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/1.md",
                "severity": "warning",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
                "live": False,
                "status": "ongoing",
            },
            {
                "message_id": "2-yyy-zzzz.md",
                "date": "2023-01-03T08:05:54+00:00",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/2.md",
                "severity": "warning",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
                "live": False,
                "status": "ongoing",
            },
            {
                "message_id": "3-yyy-zzzz.md",
                "date": "2023-01-04T08:05:54+00:00",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/3.md",
                "severity": "warning",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
                "live": False,
                "status": "ongoing",
            },
            {
                "message_id": "4-yyy-zzzz.md",
                "date": "2023-01-05T08:05:54+00:00",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/4.md",
                "severity": "warning",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
                "live": False,
                "status": "ongoing",
            },
            {
                "message_id": "5-yyy-zzzz.md",
                "date": "2023-01-05T08:05:54+00:00",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/5.md",
                "severity": "warning",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
                "live": False,
                "status": "ongoing",
            },
            {
                "message_id": "6-yyy-zzzz.md",
                "date": "2023-01-06T08:05:54+00:00",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/6.md",
                "severity": "warning",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque.",
                "live": False,
                "status": "ongoing",
            },
        ],
    }
