import datetime

import cads_catalogue.database


def get_record(id):
    return cads_catalogue.database.Resource(
        resource_id=id,
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
