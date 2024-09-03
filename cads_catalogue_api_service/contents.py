"""Custom content types (materials) API."""

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

import datetime

import fastapi

from . import dependencies, models

router = fastapi.APIRouter(
    prefix="/contents",
    tags=["contents"],
    responses={fastapi.status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get(
    "/", response_model=models.contents.Contents, response_model_exclude_none=True
)
def list_contents(
    session=fastapi.Depends(dependencies.get_session),
    site=fastapi.Depends(dependencies.get_site),
) -> models.contents.Contents:
    """Endpoint to get all contents in the material catalogue."""
    return models.contents.Contents(
        count=2,
        contents=[
            models.contents.Content(
                type="application",
                id="copernicus-interactive-climates-atlas",
                title="Copernicus Interactive Climate Atlas",
                description=(
                    "The Copernicus Interactive Climate Atlas provides graphical information "
                    "about recent past trends and future changes "
                    "(for different scenarios and global warming levels)"
                ),
                links=[
                    models.contents.Link(
                        href="https://atlas.climate.copernicus.eu/atlas",
                        rel="canonical",
                        type="text/html",
                    ),
                    models.contents.Link(
                        href="https://object-store.os-api.cci2.ecmwf.int/cci2-prod-catalogue/resources/multi-origin-c3s-atlas/overview_687312b84696878963fd72a1aa8c63162a4bb5b456e05ba6ce2619dc4324fc0a.png",  # noqa: E501
                        rel="image",
                        type="image/png",
                    ),
                ],
                published=datetime.datetime.fromisoformat("2024-02-08T11:02:31Z"),
                updated=datetime.datetime.fromisoformat("2024-02-08T11:02:31Z"),
            ),
            models.contents.Content(
                type="page",
                id="how-to-api",
                title="CDSAPI setup",
                description="Access the full data store catalogue, with search and availability features",
                links=[
                    models.contents.Link(
                        href="https://object-store.os-api.cci2.ecmwf.int/cci2-prod-catalogue/resources/multi-origin-c3s-atlas/layout_174f693ce66d6dffb033bb2b91c8e9339c6e39a72bed5b3e6cf22ce5fbd5f8ce.json",  # noqa: E501
                        rel="layout",
                        type="application/json",
                    ),
                ],
                published=datetime.datetime.fromisoformat("2024-02-08T11:02:31Z"),
                updated=datetime.datetime.fromisoformat("2024-02-08T11:02:31Z"),
            ),
        ],
    )


@router.get(
    "/{type}", response_model=models.contents.Contents, response_model_exclude_none=True
)
def list_contents_of_type(
    type: str,
    session=fastapi.Depends(dependencies.get_session),
    site=fastapi.Depends(dependencies.get_site),
) -> models.contents.Contents:
    """Endpoint to get all contents of a single type in the material catalogue."""
    contents = list_contents(session, site)
    results = [c for c in contents.contents if c.type == type]
    if not results:
        raise fastapi.HTTPException(
            status_code=404, detail=f"No contents of type {type} found"
        )
    return models.contents.Contents(count=len(results), contents=results)


@router.get(
    "/{type}/{id}",
    response_model=models.contents.Content,
    response_model_exclude_none=True,
)
def get_content(
    type: str,
    id: str,
    session=fastapi.Depends(dependencies.get_session),
    site=fastapi.Depends(dependencies.get_site),
) -> models.contents.Content:
    """Endpoint to get a content."""
    contents = list_contents(session, site)
    results = [c for c in contents.contents if c.type == type and c.id == id]
    if not results:
        raise fastapi.HTTPException(status_code=404, detail=f"Content {id} found")
    return results[0]
