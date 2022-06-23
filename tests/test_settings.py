import os

from cads_catalogue_api_service import config


def test_settings_default() -> None:
    """Test that the default settings are correct."""
    session = config.SqlalchemySettings()

    assert (
        session.connection_string
        == "postgresql://catalogue:password@localhost:5432/catalogue"
    )


def test_settings_custom() -> None:
    """Test that the default settings can be changed."""
    session = config.SqlalchemySettings()
    session.postgres_dbname = "foo"

    assert (
        session.connection_string
        == "postgresql://catalogue:password@localhost:5432/foo"
    )


def test_settings_env() -> None:
    """Test that the default settings can be taken from env vars."""
    os.environ["POSTGRES_DBNAME"] = "bar"
    session = config.SqlalchemySettings()

    assert (
        session.connection_string
        == "postgresql://catalogue:password@localhost:5432/bar"
    )
