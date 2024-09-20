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

import urllib

import cads_catalogue
import fastapi
import sqlalchemy as sa

from . import config, dependencies, models

router = fastapi.APIRouter(
    prefix="/contents",
    tags=["contents"],
    responses={fastapi.status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


def query_contents(
    session: sa.orm.Session,
    site: str,
    ctype: str | None = None,
):
    stmt = (
        sa.select(sa.func.count())
        .select_from(cads_catalogue.database.Content)
        .where(cads_catalogue.database.Content.site == site)
    )
    count = session.execute(stmt).scalar()
    stmt = (
        sa.select(cads_catalogue.database.Content)
        .where(cads_catalogue.database.Content.site == site)
        .order_by(cads_catalogue.database.Content.title)
    )
    results = session.scalars(stmt).all()
    return count, results


@router.get(
    "/", response_model=models.contents.Contents, response_model_exclude_none=True
)
def list_contents(
    session=fastapi.Depends(dependencies.get_session),
    site=fastapi.Depends(dependencies.get_site),
) -> models.contents.Contents:
    """Endpoint to get all contents in the material catalogue."""
    count, results = query_contents(session, site=site)

    return models.contents.Contents(
        count=count,
        contents=[
            models.contents.Content(
                type=content.type,
                id=content.slug,
                title=content.title,
                description=content.description,
                links=[
                    *(
                        (
                            models.contents.Link(
                                href=urllib.parse.urljoin(
                                    config.settings.document_storage_url, content.link
                                ),
                                rel="canonical",
                                type="text/html",
                            ),
                        )
                        if content.link
                        else tuple()
                    ),
                    *(
                        (
                            models.contents.Link(
                                href=urllib.parse.urljoin(
                                    config.settings.document_storage_url, content.image
                                ),
                                rel="image",
                                type="image/*",
                            ),
                        )
                        if content.image
                        else tuple()
                    ),
                    *(
                        (
                            models.contents.Link(
                                href=urllib.parse.urljoin(
                                    config.settings.document_storage_url, content.layout
                                ),
                                rel="layout",
                                type="application/json",
                            ),
                        )
                        if content.layout
                        else tuple()
                    ),
                ],
                published=content.publication_date,
                updated=content.content_update,
            )
            for content in results
        ],
    )


@router.get(
    "/{ctype}",
    response_model=models.contents.Contents,
    response_model_exclude_none=True,
)
def list_contents_of_type(
    ctype: str,
    session=fastapi.Depends(dependencies.get_session),
    site=fastapi.Depends(dependencies.get_site),
) -> models.contents.Contents:
    """Endpoint to get all contents of a single type in the material catalogue."""
    contents = list_contents(session, site)
    results = [c for c in contents.contents if c.type == ctype]
    if not results:
        raise fastapi.HTTPException(
            status_code=404, detail=f"No contents of type {type} found"
        )
    return models.contents.Contents(count=len(results), contents=results)


@router.get(
    "/{ctype}/{id}",
    response_model=models.contents.Content,
    response_model_exclude_none=True,
)
def get_content(
    ctype: str,
    id: str,
    session=fastapi.Depends(dependencies.get_session),
    site=fastapi.Depends(dependencies.get_site),
) -> models.contents.Content:
    """Endpoint to get a content."""
    contents = list_contents(session, site)
    results = [c for c in contents.contents if c.type == ctype and c.id == id]
    if not results:
        raise fastapi.HTTPException(status_code=404, detail=f"Content {id} found")
    return results[0]
