"""Custom Content Types."""

# Copyright 2024, European Union.
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

import pydantic


class Link(pydantic.BaseModel):
    """Link definition."""

    href: pydantic.HttpUrl | str
    rel: str
    type: str | None = None
    title: str | None = None


class Content(pydantic.BaseModel):
    """Content definition."""

    type: str
    id: str
    title: str
    description: str
    published: datetime.datetime
    updated: datetime.datetime
    links: list[Link] = []


class Contents(pydantic.BaseModel):
    """Contents definition."""

    count: int
    contents: list[Content]
