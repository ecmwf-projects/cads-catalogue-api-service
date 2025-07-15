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

import pydantic
import stac_fastapi.types
import stac_fastapi.types.stac
from typing_extensions import TypedDict


class LicenceCategories(str, enum.Enum):
    dataset = "dataset"
    portal = "portal"


class Licence(TypedDict):
    """Licence definition."""

    # id here is the licence slug
    id: str | None
    label: str | None
    revision: int | None
    contents_url: str
    attachment_url: str
    scope: LicenceCategories | str | None
    portal: str | None


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


class Message(pydantic.BaseModel):
    """A portal or dataset message."""

    model_config = pydantic.ConfigDict(from_attributes=True, populate_by_name=True)

    id: str | None = pydantic.Field(alias="message_uid", serialization_alias="id")
    date: datetime.datetime | None
    summary: str | None = None
    url: str | None = None
    severity: str | None
    content: str | None
    live: bool | None
    show_date: bool | None = True


class Messages(TypedDict):
    """Messages vocabulary."""

    messages: list[Message]


class Changelog(TypedDict):
    """Changelog vocabulary."""

    changelog: list[Message]


class CADSCollections(stac_fastapi.types.stac.Collections):
    """STAC collections entitiy with additional fields not (yet) in the STAC spec."""

    # Injecting elements count (waiting for STAC API to support this officially)
    # See https://github.com/radiantearth/stac-api-spec/issues/442
    numberMatched: int | None
    numberReturned: int | None
