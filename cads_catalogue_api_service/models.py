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
from typing import Any, Type, TypedDict

import stac_fastapi.types
import stac_fastapi.types.stac

DatasetBase = TypedDict(
    "DatasetBase",
    {
        "description": dict[str, Any],
        "tmp:publication_date": Type[datetime.date],
        "tmp:variables": dict[str, Any],
        "tmp:doi": str,
    },
)


class Dataset(stac_fastapi.types.stac.Collection, DatasetBase):
    """STAC based dataset.

    This class extends the OGC/STAC Collection with additional non-STAC fields.
    """


class Licence(TypedDict):
    """Licence definition."""

    # id here is the licence slug
    id: str
    label: str
    revision: int


class Licences(TypedDict):
    """Licences vocabulary."""

    licences: list[Licence]


class Keyword(TypedDict):
    """Keyword definition."""

    id: str
    label: str


class Keywords(TypedDict):
    """Keywords vocabulary."""

    keywords: list[Keyword]


class Message(TypedDict):
    """Message definition."""

    message_id: str
    date: datetime.datetime
    summary: str
    url: str | None
    severity: str
    content: str
    live: bool
    status: str


class Messages(TypedDict):
    """Messages vocabulary."""

    messages: list[Message]


class Changelog(TypedDict):
    """Changelog vocabulary."""

    changelog: list[Message]
