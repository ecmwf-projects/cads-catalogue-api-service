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

import fastapi
import fastapi.testclient

import cads_catalogue_api_service
from cads_catalogue_api_service.main import app

client = fastapi.testclient.TestClient(app)


def static_messages_query(_foo: Any) -> list[Any]:
    return [
        Any(
            message_id=1, message_uid="cc-by-4.0", title="CC-BY-4.0", date="2023-01-0T08:05:54Z",
            summary="Found a log on this dataset",url="http://object-storage/…/0.md",severity="critical",links=[]
        ),
        Any(
            message_id=2, message_uid="cc-by-4.0", title="CC-BY-4.0", date="2023-01-0T08:05:54Z",
            summary="Found a log on this dataset",url="http://object-storage/…/0.md",severity="critical",links=[]
        ),
    ]


def static_changelog_messages(_foo: Any) -> list[Any]:
    return [
        Any(
            message_id=1, message_uid="cc-by-4.0", title="CC-BY-4.0", date="2023-01-0T08:05:54Z",
            summary="Found a log on this dataset",url="http://object-storage/…/0.md",severity="critical",archived=True,links=[]
        ),
        Any(
            message_id=2, message_uid="cc-by-4.0", title="CC-BY-4.0", date="2023-01-0T08:05:54Z",
            summary="Found a log on this dataset",url="http://object-storage/…/0.md",severity="critical",archived=True,links=[]
        ),
        Any(
            message_id=3, message_uid="cc-by-4.0", title="CC-BY-4.0", date="2023-01-0T08:05:54Z",
            summary="Found a log on this dataset",url="http://object-storage/…/0.md",severity="critical",archived=True,links=[]
        ),
        Any(
            message_id=4, message_uid="cc-by-4.0", title="CC-BY-4.0", date="2023-01-0T08:05:54Z",
            summary="Found a log on this dataset",url="http://object-storage/…/0.md",severity="critical",archived=True,links=[]
        ),
        Any(
            message_id=5, message_uid="cc-by-4.0", title="CC-BY-4.0", date="2023-01-0T08:05:54Z",
            summary="Found a log on this dataset",url="http://object-storage/…/0.md",severity="critical",archived=True,links=[]
        ),
        Any(
            message_id=6, message_uid="cc-by-4.0", title="CC-BY-4.0", date="2023-01-0T08:05:54Z",
            summary="Found a log on this dataset",url="http://object-storage/…/0.md",severity="critical",archived=True,links=[]
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
        "/messages",
    )

    assert response.status_code == 200
    assert response.json() == {
        "messages": [
            {
                "id": "0-yyy-zzzz.md",
                "date": "2023-01-0T08:05:54Z",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/0.md",
                "severity": "critical",
                "archived": True,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/json",
                        "href": "<property object at 0x7f0ecfb6ccc0>",
                    }
                ],
            },
            {
                "id": "1-yyy-zzzz.md",
                "date": "2023-01-0T08:05:54Z",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/1.md",
                "severity": "critical",
                "archived": True,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/json",
                        "href": "<property object at 0x7f0ecfb6ccc0>",
                    }
                ],
            },
        ],
    }


def test_vocabularies_keywords(monkeypatch) -> None:
    monkeypatch.setattr(
        "cads_catalogue_api_service.messages.query_changelog_list",
        static_changelog_messages,
    )
    """Test list of all changelog."""
    response = client.get(
        "/messages/changelog",
    )

    assert response.status_code == 200
    assert response.json() == {
        "changelog": [
            {
                "id": "0-yyy-zzzz.md",
                "date": "2023-01-0T08:05:54Z",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/0.md",
                "severity": "warn",
                "archived": True,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/json",
                        "href": "<property object at 0x7f0ecfb6ccc0>",
                    }
                ],
            },
            {
                "id": "1-yyy-zzzz.md",
                "date": "2023-01-0T08:05:54Z",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/1.md",
                "severity": "info",
                "archived": True,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/json",
                        "href": "<property object at 0x7f0ecfb6ccc0>",
                    }
                ],
            },
            {
                "id": "2-yyy-zzzz.md",
                "date": "2023-01-0T08:05:54Z",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/2.md",
                "severity": "critical",
                "archived": True,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/json",
                        "href": "<property object at 0x7f0ecfb6ccc0>",
                    }
                ],
            },
            {
                "id": "3-yyy-zzzz.md",
                "date": "2023-01-0T08:05:54Z",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/3.md",
                "severity": "critical",
                "archived": True,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/json",
                        "href": "<property object at 0x7f0ecfb6ccc0>",
                    }
                ],
            },
            {
                "id": "4-yyy-zzzz.md",
                "date": "2023-01-0T08:05:54Z",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/4.md",
                "severity": "critical",
                "archived": True,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/json",
                        "href": "<property object at 0x7f0ecfb6ccc0>",
                    }
                ],
            },
            {
                "id": "5-yyy-zzzz.md",
                "date": "2023-01-0T08:05:54Z",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/5.md",
                "severity": "warn",
                "archived": True,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/json",
                        "href": "<property object at 0x7f0ecfb6ccc0>",
                    }
                ],
            },
            {
                "id": "6-yyy-zzzz.md",
                "date": "2023-01-0T08:05:54Z",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/6.md",
                "severity": "warn",
                "archived": True,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/json",
                        "href": "<property object at 0x7f0ecfb6ccc0>",
                    }
                ],
            },
            {
                "id": "7-yyy-zzzz.md",
                "date": "2023-01-0T08:05:54Z",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/7.md",
                "severity": "info",
                "archived": True,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/json",
                        "href": "<property object at 0x7f0ecfb6ccc0>",
                    }
                ],
            },
            {
                "id": "8-yyy-zzzz.md",
                "date": "2023-01-0T08:05:54Z",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/8.md",
                "severity": "warn",
                "archived": True,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/json",
                        "href": "<property object at 0x7f0ecfb6ccc0>",
                    }
                ],
            },
            {
                "id": "9-yyy-zzzz.md",
                "date": "2023-01-0T08:05:54Z",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/9.md",
                "severity": "info",
                "archived": True,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/json",
                        "href": "<property object at 0x7f0ecfb6ccc0>",
                    }
                ],
            },
            {
                "id": "10-yyy-zzzz.md",
                "date": "2023-01-0T08:05:54Z",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/10.md",
                "severity": "info",
                "archived": True,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/json",
                        "href": "<property object at 0x7f0ecfb6ccc0>",
                    }
                ],
            },
            {
                "id": "11-yyy-zzzz.md",
                "date": "2023-01-0T08:05:54Z",
                "summary": "Found a log on this dataset",
                "url": "http://object-storage/…/11.md",
                "severity": "info",
                "archived": True,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/json",
                        "href": "<property object at 0x7f0ecfb6ccc0>",
                    }
                ],
            },
        ],
    }
