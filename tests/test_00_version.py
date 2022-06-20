import cads_catalogue_api_service


def test_version() -> None:
    assert cads_catalogue_api_service.__version__ != "999"
