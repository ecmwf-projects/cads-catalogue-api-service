"""Custom Schema.org (Google Datasets compatibility)."""

# Copyright 2023, European Union.
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

import pydantic


class ContactPoint(pydantic.BaseModel):
    type: str = pydantic.Field("ContactPoint", const=True, alias="@type")
    contactType: str
    email: str | None = None
    url: str | None = None


class Organization(pydantic.BaseModel):
    type: str = pydantic.Field("Organization", const=True, alias="@type")
    url: str
    name: str
    logo: str | None = None
    contactPoint: ContactPoint | None = None


class DataDownload(pydantic.BaseModel):
    type: str = pydantic.Field("DataDownload", const=True, alias="@type")
    encodingFormat: str
    contentUrl: str


class GeoShape(pydantic.BaseModel):
    type: str = pydantic.Field("GeoShape", const=True, alias="@type")
    box: list[float]


class Place(pydantic.BaseModel):
    type: str = pydantic.Field("Place", const=True, alias="@type")
    geo: GeoShape


class Dataset(pydantic.BaseModel):
    context: str = pydantic.Field("https://schema.org/", const=True, alias="@context")
    type: str = pydantic.Field("Dataset", const=True, alias="@type")

    name: str
    description: str | None
    url: str | None
    # same_as: str | None = pydantic.Field(alias="sameAs")
    identifier: list[str]
    keywords: list[str]
    license: str | None
    isAccessibleForFree: bool = True
    creator: Organization
    distribution: list[DataDownload]
    temporalCoverage: str | None
    spatialCoverage: Place
    datePublished: str | None
    dateModified: str | None
    image: str | None = None

    isPartOf: list[dict] | None = None
    provider: dict | None = None
    variableMeasured: list[str] | None = None
