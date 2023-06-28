"""Catalogue Fastapi dependencies."""

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

import functools
from typing import Iterator

import fastapi
import sqlalchemy

from . import config, fastapisessionmaker


@functools.lru_cache()
def get_sessionmaker() -> fastapisessionmaker.FastAPISessionMaker:
    """Generate a DB session using fastapi_utils."""
    connection_string = config.dbsettings.connection_string
    return fastapisessionmaker.FastAPISessionMaker(connection_string)


def get_session() -> Iterator[sqlalchemy.orm.Session]:
    """Fastapi dependency that provides a sqlalchemy session."""
    yield from get_sessionmaker().get_db()


def get_portals_values(portal: str) -> list[str]:
    portals = [p.strip() for p in portal.split(",")] if portal else None
    return portals


def get_portals(
    portal=fastapi.Header(default=None, alias=config.PORTAL_HEADER_NAME)
) -> str | None:
    """Fastapi dependency that provides the CADS portal profile."""
    portals = get_portals_values(portal)
    return portals
