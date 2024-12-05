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

import fastapi

from . import dependencies, search_utils

router = fastapi.APIRouter(
    prefix="",
    tags=["typeahead"],
    responses={fastapi.status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
    include_in_schema=False,
)


@router.get("/typeahead")
def typeahead(
    session=fastapi.Depends(dependencies.get_session),
    portals: list[str] | None = fastapi.Depends(dependencies.get_portals),
    chars: str = fastapi.Query(..., min_length=2, max_length=50),
) -> list[str]:
    """Typeahead for CADS webportal search feature."""
    search = search_utils.apply_filters_typeahead(
        session, chars, search=None, portals=portals
    )
    result = session.execute(search)
    return result.scalars().all()
