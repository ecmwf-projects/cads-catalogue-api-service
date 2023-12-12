"""Custom models that extends the OGC/STAC ones."""

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

import datetime
import enum
from typing import TypedDict


class LicenceCategories(str, enum.Enum):
    dataset: str = "dataset"
    portal: str = "portal"


class Licence(TypedDict):
    """Licence definition."""

    # id here is the licence slug
    id: str | None
    label: str | None
    revision: int | None
    contents_url: str
    attachment_url: str
    scope: LicenceCategories | str | None


class Licences(TypedDict):
    """Licences vocabulary."""

    licences: list[Licence]


class Keyword(TypedDict):
    """Keyword definition."""

    id: str | None
    label: str | None


class Keywords(TypedDict):
    """Keywords vocabulary."""

    keywords: list[Keyword]


class Message(TypedDict):
    """Message definition."""

    id: str | None
    date: datetime.datetime | None
    summary: str | None
    url: str | None
    severity: str | None
    content: str | None
    live: bool | None


class Messages(TypedDict):
    """Messages vocabulary."""

    messages: list[Message]


class Changelog(TypedDict):
    """Changelog vocabulary."""

    changelog: list[Message]
