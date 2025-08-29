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

import cads_catalogue.database
import pytest
from testing import Request, generate_expected, get_record

import cads_catalogue_api_service.client
import cads_catalogue_api_service.models
from cads_catalogue_api_service.models.stac import CadsSanityCheck, SanityCheckStatus


def fake_get_active_message(
    *args, **kwargs
) -> cads_catalogue_api_service.models.Message:
    return cads_catalogue_api_service.models.Message(
        message_uid="message-2",
        date=datetime.datetime(2024, 1, 1, 12, 15, 34),
        content="Message 2",
        severity="warning",
        live=True,
    )


def fake_process_sanity_check(*args, **kwargs) -> CadsSanityCheck:
    return CadsSanityCheck(
        status=SanityCheckStatus.AVAILABLE,
        timestamp=datetime.datetime(2024, 1, 1, 12, 15, 34),
    )


def test_collection_serializer(monkeypatch) -> None:
    """Test serialization from db record to STAC."""
    monkeypatch.setattr(
        "cads_catalogue_api_service.client.get_active_message",
        fake_get_active_message,
    )
    monkeypatch.setattr(
        "cads_catalogue_api_service.client.sanity_check.process",
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


def test_collection_serializer_licences(monkeypatch) -> None:
    """Test serialization of licenses from db record to STAC."""
    monkeypatch.setattr(
        "cads_catalogue_api_service.client.get_active_message",
        fake_get_active_message,
    )
    monkeypatch.setattr(
        "cads_catalogue_api_service.client.sanity_check.process",
        fake_process_sanity_check,
    )
    request = Request("https://mycatalogue.org/")
    record = get_record("era5-something")

    # Test with multiple licences, should be "other"
    record.licences = [
        cads_catalogue.database.Licence(
            licence_id="licence-1",
            revision=1,
            title="Licence 1",
            download_filename="licences/licence1.docx",
        ),
        cads_catalogue.database.Licence(
            licence_id="licence-2",
            revision=1,
            title="Licence 2",
            download_filename="licences/licence2.docx",
        ),
    ]
    stac_record = cads_catalogue_api_service.client.collection_serializer(
        record, session=object(), request=request
    )
    assert stac_record["license"] == "other"

    # Test with a single licence with spdx_identifier
    record.licences = [
        cads_catalogue.database.Licence(
            licence_id="licence-1",
            revision=1,
            title="Licence 1",
            download_filename="licences/licence1.docx",
            spdx_identifier="CC-BY-4.0",
        )
    ]
    stac_record = cads_catalogue_api_service.client.collection_serializer(
        record, session=object(), request=request
    )
    assert stac_record["license"] == "CC-BY-4.0"

    # Test with a single licence without spdx_identifier, should be "other"
    record.licences = [
        cads_catalogue.database.Licence(
            licence_id="licence-1",
            revision=1,
            title="Licence 1",
            download_filename="licences/licence1.docx",
        )
    ]
    stac_record = cads_catalogue_api_service.client.collection_serializer(
        record, session=object(), request=request
    )
    assert stac_record["license"] == "other"

    # Test with a single licence with spdx_identifier in preview mode
    record.licences = [
        cads_catalogue.database.Licence(
            licence_id="licence-1",
            revision=1,
            title="Licence 1",
            download_filename="licences/licence1.docx",
            spdx_identifier="MIT",
        )
    ]
    stac_record = cads_catalogue_api_service.client.collection_serializer(
        record, session=object(), request=request, preview=True
    )
    assert stac_record["license"] == "MIT"

    # Test with no licences, should be "other"
    record.licences = []
    stac_record = cads_catalogue_api_service.client.collection_serializer(
        record, session=object(), request=request
    )
    assert stac_record["license"] == "other"


@pytest.mark.parametrize(
    "update_frequency",
    [
        (None),
        ("threeTimesAYear"),
    ],
)
def test_update_frequency(monkeypatch, update_frequency: str | None) -> None:
    """Test cads:update_frequency properly shown on STAC."""
    monkeypatch.setattr(
        "cads_catalogue_api_service.client.get_active_message",
        fake_get_active_message,
    )
    monkeypatch.setattr(
        "cads_catalogue_api_service.client.sanity_check.process",
        fake_process_sanity_check,
    )
    request = Request("https://mycatalogue.org/")
    record = get_record("era5-something", update_frequency=update_frequency)
    stac_record = cads_catalogue_api_service.client.collection_serializer(
        record, session=object(), request=request
    )
    assert stac_record.get("cads:update_frequency") == update_frequency
