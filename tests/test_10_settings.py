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
