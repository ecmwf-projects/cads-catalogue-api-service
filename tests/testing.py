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
import urllib

import cads_catalogue.database


class Request:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def url_for(self, name: str, **kwargs: str) -> str:
        return "/collections"


def get_record(id: str) -> cads_catalogue.database.Resource:
    return cads_catalogue.database.Resource(
        resource_uid=id,
        title="ERA5",
        description={
            "file-format": "GRIB",
            "data-type": "Gridded",
            "projection": "Regular latitude-longitude grid.",
        },
        abstract="Lorem ipsum dolor",
        form="resources/reanalysis-era5-pressure-levels/form.json",
        constraints="resources/reanalysis-era5-pressure-levels/constraints.json",
        keywords=["label 1", "label 2"],
        variables=["var1", "var2"],
        geo_extent={"bboxN": 50, "bboxW": -0.5, "bboxS": 45, "bboxE": 15},
        begin_date=datetime.date(1980, 1, 1),
        doi="11.2222/cads.12345",
        documentation=[
            {
                "url": "https://rtd.org/foo-bar",
                "title": "ERA5 data documentation",
                "description": (
                    "Detailed information relating to the ERA5 data archive "
                    "can be found in the web link above."
                ),
            }
        ],
        publication_date=datetime.datetime.strptime(
            "2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"
        ),
        record_update=datetime.datetime.strptime(
            "2020-02-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"
        ),
        resource_update=datetime.datetime.strptime(
            "2020-02-05T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"
        ),
        licences=[
            cads_catalogue.database.Licence(
                licence_id="creative-commons",
                revision=2,
                title="Creative Commons Attribution 4.0 International",
                download_filename="licences/license.docx",
            )
        ],
        related_resources=[
            cads_catalogue.database.Resource(
                resource_uid="another-dataset", title="Yet another dataset"
            )
        ],
    )


def generate_expected(
    base_url="http://foo.org/", document_storage_url="/document-storage/", preview=False
) -> dict:
    expected = {
        "type": "Collection",
        "id": "era5-something",
        "stac_version": "1.0.0",
        "title": "ERA5",
        "description": "Lorem ipsum dolor",
        "keywords": ["label 1", "label 2"],
        "license": "proprietary",
        "extent": {
            "spatial": {"bbox": [[-0.5, 45.0, 50.0, 15.0]]},
            "temporal": {"interval": [["1980-01-01T00:00:00Z", None]]},
        },
        "links": [
            {
                "rel": "self",
                "type": "application/json",
                "href": urllib.parse.urljoin(base_url, "collections/era5-something"),
            },
            {
                "rel": "parent",
                "type": "application/json",
                "href": base_url,
            },
            {
                "rel": "root",
                "type": "application/json",
                "href": base_url,
            },
            {
                "rel": "license",
                "href": urllib.parse.urljoin(
                    base_url,
                    f"{document_storage_url}licences/license.docx",
                ),
                "title": "Creative Commons Attribution 4.0 International",
            },
        ]
        + (
            []
            if preview
            else [
                {
                    "rel": "describedby",
                    "href": "https://rtd.org/foo-bar",
                    "title": "ERA5 data documentation",
                },
                {
                    "rel": "form",
                    "href": urllib.parse.urljoin(
                        base_url,
                        f"{document_storage_url}resources/reanalysis-era5-pressure-levels/form.json",
                    ),
                    "type": "application/json",
                },
                {
                    "rel": "constraints",
                    "href": urllib.parse.urljoin(
                        base_url,
                        f"{document_storage_url}resources/reanalysis-era5-pressure-levels/constraints.json",
                    ),
                    "type": "application/json",
                },
                {
                    "rel": "retrieve",
                    "href": urllib.parse.urljoin(
                        base_url, "api/processing/processes/era5-something"
                    ),
                    "type": "application/json",
                },
                {
                    "rel": "related",
                    "href": urllib.parse.urljoin(
                        base_url, "/collections/another-dataset"
                    ),
                    "title": "Yet another dataset",
                },
                {
                    "rel":"messages",
                    "href":urllib.parse.urljoin(base_url, "collections/era5-something/messages"),
                    "title":"All messages related to the selected dataset"
                },
                {
                    "rel":"changelog",
                    "href":urllib.parse.urljoin(base_url, "collections/era5-something/messages/changelog"),
                    "title":"All archived messages related to the selected dataset"
                }
            ]
        ),
        "published": "2020-01-01T00:00:00Z",
        "sci:doi": "11.2222/cads.12345",
    }
    if not preview:
        expected = {
            **expected,
        }
    return expected
