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
def get_sessionmaker(read_only=True) -> fastapisessionmaker.FastAPISessionMaker:
    """Generate a DB session using fastapi_utils."""
    if read_only:
        connection_string = config.dbsettings.connection_string_read
    else:
        connection_string = config.dbsettings.connection_string
    return fastapisessionmaker.FastAPISessionMaker(connection_string)


def get_session() -> Iterator[sqlalchemy.orm.Session]:
    """Fastapi dependency that provides a sqlalchemy read-only session."""
    yield from get_sessionmaker(read_only=True).get_db()


def get_session_rw() -> Iterator[sqlalchemy.orm.Session]:
    """Fastapi dependency that provides a sqlalchemy read&write session."""
    yield from get_sessionmaker(read_only=False).get_db()


def get_portals_values(portal: str | None) -> list[str] | None:
    portals = [p.strip() for p in portal.split(",")] if portal else None
    return portals


def get_portals(
    portal=fastapi.Header(default=None, alias=config.PORTAL_HEADER_NAME),
) -> list[str] | None:
    """Fastapi dependency that provides the CADS portal profile."""
    portals = get_portals_values(portal)
    return portals


def get_site(
    site=fastapi.Header(default=None, alias=config.SITE_HEADER_NAME),
) -> list[str] | None:
    """Fastapi dependency that provides the CADS portal profile."""
    return site
