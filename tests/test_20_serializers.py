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

from testing import get_record

import cads_catalogue_api_service.main


def test_collection_serializer() -> None:
    """Test serialization from db record to STAC."""
    base_url = "https://mycatalogue.org/catalogue"
    record = get_record("era5-something")
    stac_record = cads_catalogue_api_service.main.collection_serializer(
        record, base_url
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
