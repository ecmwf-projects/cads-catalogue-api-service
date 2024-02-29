# Copyright 2024, European Union.
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

import cads_catalogue_api_service


def test_get_portals_values():
    assert cads_catalogue_api_service.dependencies.get_portals_values(
        portal="foo,bar"
    ) == [
        "foo",
        "bar",
    ]

    assert (
        cads_catalogue_api_service.dependencies.get_portals_values(portal=None) is None
    )
