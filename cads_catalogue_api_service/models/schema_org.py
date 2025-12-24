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

from typing import Literal

import pydantic


class ContactPoint(pydantic.BaseModel):
    type: Literal["ContactPoint"] = pydantic.Field(
        default="ContactPoint", alias="@type"
    )
    contactType: str
    email: str | None = None
    url: str | None = None


class Organization(pydantic.BaseModel):
    type: Literal["Organization"] = pydantic.Field(
        default="Organization", alias="@type"
    )
    url: str
    name: str
    logo: str | None = None
    contactPoint: ContactPoint | None = None


class DataDownload(pydantic.BaseModel):
    type: Literal["DataDownload"] = pydantic.Field(
        default="DataDownload", alias="@type"
    )
    encodingFormat: str
    url: str | None = None
    contentSize: str | None


class GeoShape(pydantic.BaseModel):
    type: Literal["GeoShape"] = pydantic.Field(default="GeoShape", alias="@type")
    box: list[float]


class Place(pydantic.BaseModel):
    type: Literal["Place"] = pydantic.Field(default="Place", alias="@type")
    geo: GeoShape


class Dataset(pydantic.BaseModel):
    """Schema.org representation of a dataset.

    See https://schema.org/Dataset
    """

    context: Literal["https://schema.org/"] = pydantic.Field(
        default="https://schema.org/", alias="@context"
    )
    type: Literal["Dataset"] = pydantic.Field(default="Dataset", alias="@type")

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
    conditionsOfAccess: str | None
    isPartOf: list[dict] | None = None
    contentSize: str | None = None
    isBasedOn: list[str] | None = None
