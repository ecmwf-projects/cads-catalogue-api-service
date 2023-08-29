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

import pydantic


class LicenceCategories(str, enum.Enum):
    dataset: str = "dataset"
    portal: str = "portal"


class Licence(TypedDict):
    """Licence definition."""

    # id here is the licence slug
    id: str
    label: str
    revision: int
    contents_url: str
    attachment_url: str
    scope: LicenceCategories


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

    id: str
    date: datetime.datetime
    summary: str | None
    url: str | None
    severity: str
    content: str
    live: bool


class Messages(TypedDict):
    """Messages vocabulary."""

    messages: list[Message]


class Changelog(TypedDict):
    """Changelog vocabulary."""

    changelog: list[Message]


class SchemaOrgContactPoint(pydantic.BaseModel):
    type: str = pydantic.Field("ContactPoint", const=True, alias="@type")
    contact_type: str = pydantic.Field(alias="contactType")
    email: str
    url: str


class SchemaOrgOrganization(pydantic.BaseModel):
    type: str = pydantic.Field("Organization", const=True, alias="@type")
    url: str
    name: str
    logo: str
    contact_point: SchemaOrgContactPoint | None = None


class SchemaOrgDataDownload(pydantic.BaseModel):
    type: str = pydantic.Field("DataDownload", const=True, alias="@type")
    encoding_format: str = pydantic.Field(alias="encodingFormat")
    content_url: str = pydantic.Field(alias="contentUrl")


class SchemaOrgGeoShape(pydantic.BaseModel):
    type: str = pydantic.Field("GeoShape", const=True, alias="@type")
    box: list[float]


class SchemaOrgPlace(pydantic.BaseModel):
    type: str = pydantic.Field("Place", const=True, alias="@type")
    geo: SchemaOrgGeoShape


class SchemaOrgDataset(pydantic.BaseModel):
    context: str = pydantic.Field("https://schema.org/", const=True, alias="@context")
    type: str = pydantic.Field("Dataset", const=True, alias="@type")

    name: str
    description: str | None
    url: str | None
    same_as: str | None = pydantic.Field(alias="sameAs")
    identifier: list[str]
    keywords: list[str]
    license: str | None
    is_accessible_for_free: bool = True
    creator: SchemaOrgOrganization
    distribution: list[SchemaOrgDataDownload]
    temporalCoverage: str | None
    spatialCoverage: SchemaOrgPlace
    dateModified: str | None
    thumbnailUrl: str | None = None
