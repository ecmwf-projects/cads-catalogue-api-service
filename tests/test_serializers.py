import datetime

import cads_catalogue.database

import cads_catalogue_api_service.serializers


def test_collection_serializer() -> None:
    """Test serialization from db record to STAC."""
    base_url = "https://mycatalogue.org/catalogue"
    record = cads_catalogue.database.Resource(
        resource_id="era5-something",
        title="ERA5",
        description={"description": "aaaa"},
        abstract="Lorem ipsum dolor",
        contact=["aaaa", "bbbb"],
        form="form",
        citation="",
        keywords=["label 1", "label 2"],
        version="1.0.0",
        variables=["var1", "var2"],
        providers=["provider 1", "provider 2"],
        extent=[[-180, 180], [-90, 90]],
        links=[{"rel": "foo", "href": "http://foo.com"}],
        documentation="documentation",
        previewimage="img",
        publication_date=datetime.datetime.strptime(
            "2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"
        ),
        record_update=datetime.datetime.strptime(
            "2020-02-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"
        ),
        resource_update=datetime.datetime.strptime(
            "2020-02-05T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"
        ),
    )
    stac_record = (
        cads_catalogue_api_service.serializers.CollectionSerializer.db_to_stac(
            record, base_url
        )
    )

    assert stac_record == {
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
