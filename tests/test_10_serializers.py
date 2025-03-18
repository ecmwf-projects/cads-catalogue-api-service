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

from testing import Request, generate_expected, get_record

import cads_catalogue_api_service.client
import cads_catalogue_api_service.models
from cads_catalogue_api_service.client import SanityCheckStatus


def fake_get_active_message(*args, **kwargs) -> None:
    return cads_catalogue_api_service.models.Message(
        id="message-2",
        date=datetime.datetime(2024, 1, 1, 12, 15, 34),
        content="Message 2",
        severity="warning",
        live=True,
    )


def fake_process_sanity_check(*args, **kwargs) -> dict[str, str | None]:
    return {
        "status": SanityCheckStatus.available,
        "timestamp": None,
    }


def test_collection_serializer(monkeypatch) -> None:
    """Test serialization from db record to STAC."""
    monkeypatch.setattr(
        "cads_catalogue_api_service.client.get_active_message",
        fake_get_active_message,
    )
    monkeypatch.setattr(
        "cads_catalogue_api_service.client.process_sanity_check",
        fake_process_sanity_check,
    )
    request = Request("https://mycatalogue.org/")  # note the final slash!
    record = get_record("era5-something")
    stac_record = cads_catalogue_api_service.client.collection_serializer(
        record, session=object(), request=request
    )

    assert stac_record == generate_expected(request.base_url)

    stac_record = cads_catalogue_api_service.client.collection_serializer(
        record, session=object(), request=request, preview=True
    )

    assert stac_record == generate_expected(request.base_url, preview=True)

    stac_record = cads_catalogue_api_service.client.collection_serializer(
        record, session=object(), request=request, schema_org=True
    )

    assert stac_record == generate_expected(request.base_url, schema_org=True)


def test_hidden(monkeypatch) -> None:
    """Test cads:hidden properly shown on STAC."""
    monkeypatch.setattr(
        "cads_catalogue_api_service.client.get_active_message",
        fake_get_active_message,
    )
    request = Request("https://mycatalogue.org/")  # note the final slash!
    record = get_record("era5-something")
    stac_record = cads_catalogue_api_service.client.collection_serializer(
        record, session=object(), request=request
    )

    assert "cads:hidden" not in stac_record

    record = get_record("era5-something", hidden=True)
    stac_record = cads_catalogue_api_service.client.collection_serializer(
        record, session=object(), request=request
    )

    assert stac_record["cads:hidden"] is True
