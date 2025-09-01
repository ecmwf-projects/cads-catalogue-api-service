"""Custom models that extends the STAC ones."""

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
import enum
from typing import Any

import pydantic
import stac_fastapi.types.stac
from typing_extensions import NotRequired, TypedDict


class SanityCheckStatus(str, enum.Enum):
    """Sanity check status enumerator."""

    AVAILABLE = "available"
    WARNING = "warning"
    DOWN = "down"
    UNKNOWN = "unknown"
    EXPIRED = "expired"


class CadsSanityCheck(pydantic.BaseModel):
    """ECMWF DSS specific sanity check information."""

    status: SanityCheckStatus
    timestamp: datetime.datetime | None

    @pydantic.field_serializer("timestamp")
    def serialize_timestamp(self, value: datetime.datetime | None) -> str | None:
        """Serialize timestamp in ISO format with UTC 'Z' suffix."""
        if value is None:
            return None

        # Force UTC with 'Z'
        if value.tzinfo is None:
            utc_value = value.replace(tzinfo=datetime.timezone.utc)
        else:
            utc_value = value.astimezone(datetime.timezone.utc)

        return utc_value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class Collection(stac_fastapi.types.stac.Collection):
    """STAC Collection with additional ECMWF DSS fields."""

    cads_sanity_check: CadsSanityCheck = pydantic.Field(alias="cads:sanity_check")


class Collections(TypedDict):
    """All collections endpoint.

    https://github.com/radiantearth/stac-api-spec/tree/master/collections
    """

    collections: list[
        Collection
    ]  # Overwrite from base stac_fastapi.types.stac.Collections
    links: list[dict[str, Any]]
    numberMatched: NotRequired[int]
    numberReturned: NotRequired[int]

    # search stats
    search: NotRequired[dict[str, Any]]
