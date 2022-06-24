import cads_catalogue_api_service.config
import cads_catalogue_api_service.session


def test_session_creation() -> None:
    """Test that the default settings are correct."""
    settings = cads_catalogue_api_service.config.SqlalchemySettings()
    session = cads_catalogue_api_service.session.Session.create_from_settings(settings)

    assert session.conn_string == settings.connection_string
