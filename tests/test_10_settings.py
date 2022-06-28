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

import os

import cads_catalogue_api_service.config


def test_settings_default() -> None:
    """Test that the default settings are correct."""
    settings = cads_catalogue_api_service.config.SqlalchemySettings()
    expected_conn_string = "postgresql://catalogue:password@localhost:5432/catalogue"

    assert settings.connection_string == expected_conn_string


def test_settings_custom() -> None:
    """Test that the default settings can be changed."""
    settings = cads_catalogue_api_service.config.SqlalchemySettings()
    expected_conn_string = "postgresql://catalogue:password@localhost:5432/foo"

    settings.postgres_dbname = "foo"

    assert settings.connection_string == expected_conn_string


def test_settings_env() -> None:
    """Test that the default settings can be taken from env vars."""
    os.environ["POSTGRES_DBNAME"] = "bar"
    expected_conn_string = "postgresql://catalogue:password@localhost:5432/bar"
    settings = cads_catalogue_api_service.config.SqlalchemySettings()

    assert settings.connection_string == expected_conn_string
