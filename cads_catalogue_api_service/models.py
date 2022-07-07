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
from typing import Any, Type, TypedDict

import stac_fastapi.types

# class Dataset(stac_fastapi.types.stac.Collection):
#     """Dataset, extention of STAC Collection."""

#     publication_date: Type[datetime.date] = None
#     # redefinition of description from stac_fastapi.types.stac.Catalog, which is an str
#     description: dict[str, Any]
#     variables: dict[str, Any]


DatasetBase = TypedDict(
    "DatasetBase",
    {
        "description": dict[str, Any],
        "tmp:publication_date": Type[datetime.date],
        "tmp:variables": dict[str, Any],
    },
)


class Dataset(stac_fastapi.types.stac.Collection, DatasetBase):
    pass
