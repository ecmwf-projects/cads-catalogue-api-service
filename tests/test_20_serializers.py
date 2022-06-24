from testing import get_record

import cads_catalogue_api_service.serializers


def test_collection_serializer() -> None:
    """Test serialization from db record to STAC."""
    base_url = "https://mycatalogue.org/catalogue"
    record = get_record("era5-something")
    stac_record = (
        cads_catalogue_api_service.serializers.CollectionSerializer.db_to_stac(
            record, base_url
        )
    )
    expected = {
        "type": "Collection",
        "id": "era5-something",
        "stac_version": "1.0.0",
        "title": "ERA5",
        "description": {"description": "aaaa"},
        "keywords": ["label 1", "label 2"],
        "providers": ["provider 1", "provider 2"],
        "summaries": None,
        "extent": [[-180, 180], [-90, 90]],
        "links": [
            {
                "rel": "self",
                "type": "application/json",
                "href": "https://mycatalogue.org/collections/era5-something",
            },
            {
                "rel": "parent",
                "type": "application/json",
                "href": "https://mycatalogue.org/catalogue",
            },
            {
                "rel": "root",
                "type": "application/json",
                "href": "https://mycatalogue.org/catalogue",
            },
            {"rel": "foo", "href": "http://foo.com"},
        ],
    }

    assert stac_record == expected
