from fastapi.testclient import TestClient

from cads_catalogue_api_service import main

client = TestClient(main.app)


def test_error_handler() -> None:
    """Test that an HTTP 501 is returned in case of not implemented (but still valid) STAC routes."""
    response = client.get("/collections/a-dataset/items")
    assert response.status_code == 501
    response = client.get("/collections/a-dataset/items/ad-item")
    assert response.status_code == 501
