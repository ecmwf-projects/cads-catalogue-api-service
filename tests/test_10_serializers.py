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

from testing import Request, generate_expected, get_record

import cads_catalogue_api_service.client


def test_collection_serializer() -> None:
    """Test serialization from db record to STAC."""
    request = Request("https://mycatalogue.org/")  # note the final slash!
    record = get_record("era5-something")
    stac_record = cads_catalogue_api_service.client.collection_serializer(
        record, request=request
    )

    assert stac_record == generate_expected(request.base_url)

    stac_record = cads_catalogue_api_service.client.collection_serializer(
        record, request=request, preview=True
    )

    assert stac_record == generate_expected(request.base_url, preview=True)
