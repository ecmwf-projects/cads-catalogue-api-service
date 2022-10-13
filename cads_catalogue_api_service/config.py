"""Configuration of the service.

Options are based on pydantic.BaseSettings, so they automatically get values from the environment.
"""

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

import cads_catalogue.config
import pydantic
import stac_fastapi.types.config

MAX_LIMIT = 50


class SqlalchemySettings(stac_fastapi.types.config.ApiSettings):  # type: ignore
    """Postgres-specific API settings."""

    # Fields which are defined by STAC but not included in the database model
    forbidden_fields: set[str] = {"type"}

    # Fields which are item properties but indexed as distinct fields in the database model
    indexed_fields: set[str] = {"datetime"}

    @property
    def connection_string(self) -> str:
        """Create reader psql connection string."""
        return cads_catalogue.config.ensure_settings().connection_string


class Settings(pydantic.BaseSettings):
    """Other general settings.

    - ``document_storage_url``: Base URI to identify the document storage
    """

    document_storage_url: str = "/document-storage/"
    processes_base_url: str = "/api/processing/"


dbsettings = SqlalchemySettings()
settings = Settings()
