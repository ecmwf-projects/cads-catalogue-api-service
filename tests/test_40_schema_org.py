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

import datetime
from typing import Any

import fastapi
import fastapi.testclient
import stac_fastapi.types
import stac_fastapi.types.core

from cads_catalogue_api_service.main import app

client = fastapi.testclient.TestClient(app)


def static_collection_query(
    session: Any,
    request: Any,
    collection_id: str | None = None,
) -> stac_fastapi.types.stac.Collection:
    return {
        "type": "Collection",
        "id": "era5-something",
        "stac_version": "1.1.0",
        "title": "Era5 name",
        "description": "This dataset provides a modelled time series of gridded river discharge.",
        "keywords": [
            "Temporal coverage: Past",
        ],
        "keywords_urls": [
            "http://purl.oclc.org/NET/ssnx/cf/cf-feature",
        ],
        "license": "other",
        "extent": {
            "spatial": {"bbox": [[0, -70, 70, 360]]},
            "temporal": {
                "interval": [
                    [
                        datetime.datetime.strptime(
                            "2019-11-05T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"
                        ),
                        datetime.datetime.strptime(
                            "2023-06-22T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"
                        ),
                    ]
                ]
            },
        },
        "links": [
            {
                "rel": "self",
                "type": "application/json",
                "href": "http://localhost:8080/api/catalogue/v1/collections/era5-something",
            },
            {
                "rel": "parent",
                "type": "application/json",
                "href": "http://localhost:8080/api/catalogue/v1/",
            },
            {
                "rel": "root",
                "type": "application/json",
                "href": "http://localhost:8080/api/catalogue/v1/",
            },
            {
                "rel": "related",
                "href": "http://localhost:8080/api/catalogue/v1/collections/era5-something",
                "title": "River discharge and related historical data ",
            },
            {
                "rel": "messages",
                "href": "http://localhost:8080/api/catalogue/v1/collections/era5-something/messages",
                "title": "All messages related to the selected dataset",
            },
            {
                "rel": "changelog",
                "href": "http://localhost:8080/api/catalogue/v1/collections/era5-something/messages/changelog",
                "title": "All archived messages related to the selected dataset",
            },
            {
                "rel": "layout",
                "href": "http://localhost:8080/api/catalogue/v1/collections/era5-something/layout",
                "title": "Distribution",
            },
            {
                "rel": "retrieve",
                "href": "http://localhost:8080/api/retrieve/v1/processes/era5-something",
                "title": "Retrieve",
            },
        ],
        "assets": {
            "thumbnail": {
                "href": "https://s3.cds.org.int/swift/v1/AUTH_3e237111c3a144df8e0e0980577062b4/cds2-dev-catalogue/resources/era5-something/overview_36fc7b601512e3619bc5ba70ae0488b911d9d74e203400f9a321f5745768f6a5.png",
                "type": "image/jpg",
                "roles": ["thumbnail"],
            }
        },
        "creator_name": "Org",
        "creator_url": "https://www.org.it/",
        "creator_type": "Organization",
        "creator_contact_email": "https://support.org.it",
        "file_format": "",
        "published": "2020-05-19T00:00:00Z",
        "updated": "2023-06-22T00:00:00Z",
        "sci:doi": "10.24381/cds.ff2aef70",
        "metadata_urls": [
            "http://cfconventions.org/documents.html",
        ],
    }


def test_schema_org_jsonId(monkeypatch) -> None:
    monkeypatch.setattr(
        "cads_catalogue_api_service.schema_org.query_collection",
        static_collection_query,
    )
    monkeypatch.setenv("CDS_PROJECT_URL", "https://cds.climate.copernicus.eu")

    response = client.get(
        "/collections/era5-something/schema.org",
        headers={"X-CADS-Site": "cds"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "@context": "https://schema.org/",
        "@type": "Dataset",
        "name": "Era5 name",
        "description": "This dataset provides a modelled time series of gridded river discharge.",
        "url": "http://localhost:8080/api/catalogue/v1/collections/era5-something",
        "identifier": ["https://doi.org/10.24381/cds.ff2aef70"],
        "keywords": [
            "http://purl.oclc.org/NET/ssnx/cf/cf-feature",
        ],
        "isAccessibleForFree": True,
        "creator": {
            "@type": "Organization",
            "url": "https://www.org.it/",
            "name": "Org",
            "contactPoint": {
                "@type": "ContactPoint",
                "contactType": "User support",
                "email": "https://support.org.it",
                "url": "https://support.org.it",
            },
        },
        "distribution": [
            {
                "@type": "DataDownload",
                "encodingFormat": "application/octet-stream",
                "url": "http://localhost:8080/api/retrieve/v1/processes/era5-something",
            },
            {
                "@type": "DataDownload",
                "encodingFormat": "application/octet-stream",
                "url": "https://cds.climate.copernicus.eu/datasets/era5-something?tab=download",
            },
        ],
        "temporalCoverage": "2019-11-05T00:00:00Z/2023-06-22T00:00:00Z",
        "spatialCoverage": {
            "@type": "Place",
            "geo": {"@type": "GeoShape", "box": [0.0, -70.0, 70.0, 360.0]},
        },
        "dateModified": "2023-06-22T00:00:00Z",
        "datePublished": "2020-05-19T00:00:00Z",
        "image": "https://s3.cds.org.int/swift/v1/AUTH_3e237111c3a144df8e0e0980577062b4/cds2-dev-catalogue/resources/era5-something/overview_36fc7b601512e3619bc5ba70ae0488b911d9d74e203400f9a321f5745768f6a5.png",
        "conditionsOfAccess": "Free access upon acceptance of applicable licences and terms of use",
        "isPartOf": [
            {
                "@type": "DataCatalog",
                "identifier": "cds",
                "name": "Climate Data Store",
                "url": "https://cds.climate.copernicus.eu/datasets",
            }
        ],
        "isBasedOn": [
            "http://cfconventions.org/documents.html",
        ],
    }
