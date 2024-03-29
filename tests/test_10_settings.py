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


def test_sqlsettings_env() -> None:
    """Test that the default SQL settings can be taken from env vars."""
    os.environ["CATALOGUE_DB_HOST"] = "host1"
    os.environ["CATALOGUE_DB_HOST_READ"] = "host2"
    settings = cads_catalogue_api_service.config.SqlalchemySettings()

    assert "host1" in settings.connection_string
    assert "host2" in settings.connection_string_read


def test_settings_env() -> None:
    """Test that the default settings can be taken from env vars."""
    os.environ["DOCUMENT_STORAGE_URL"] = "http://documentstorage.net"
    expected_url = "http://documentstorage.net"
    settings = cads_catalogue_api_service.config.Settings()

    assert settings.document_storage_url == expected_url
