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

import cads_catalogue_api_service.client


def test_get_reference() -> None:
    SITE = "https://mysite.org/"
    reference = {"content": "https://foo.org/something.rst", "url": None}

    assert cads_catalogue_api_service.client.get_reference(reference, SITE) == {
        "href": "https://foo.org/something.rst",
        "rel": "reference",
        "title": None,
    }

    reference = {
        "content": "something.rst",
    }

    assert cads_catalogue_api_service.client.get_reference(reference, SITE) == {
        "href": "https://mysite.org/something.rst",
        "rel": "reference",
        "title": None,
    }


def test_get_reference_external() -> None:
    SITE = "https://mysite.org/"
    reference = {"content": None, "url": "https://foo.org/something.pdf"}

    assert cads_catalogue_api_service.client.get_reference(reference, SITE) == {
        "href": "https://foo.org/something.pdf",
        "rel": "external",
        "title": None,
    }
