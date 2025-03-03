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

from . import config, dependencies, extensions, models

router = fastapi.APIRouter(
    prefix="/contents",
    tags=["contents"],
    responses={fastapi.status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


def _apply_common_filters(query, site: str, ctype: str | None = None):
    return query.where(
        cads_catalogue.database.Content.site == site,
        cads_catalogue.database.Content.hidden.is_(False),
        *((cads_catalogue.database.Content.type == ctype,) if ctype else tuple()),
    )


def get_sorting_clause(sort: str) -> tuple:
    supported_sorts = {
        "title": (cads_catalogue.database.Content.title, sa.asc),
        "publication": (cads_catalogue.database.Content.publication_date, sa.desc),
        "update": (cads_catalogue.database.Content.content_update, sa.desc),
    }
    return supported_sorts.get(sort) or supported_sorts["title"]


def query_contents(
    session: sa.orm.Session,
    site: str,
    ctype: str | None = None,
    sortby: str = "title",
):
    """Perform a database query for multiple contents, ideally filtereb by type."""
    stmt_count = _apply_common_filters(
        sa.select(sa.func.count()).select_from(cads_catalogue.database.Content),
        site,
        ctype,
    )
    count = session.execute(stmt_count).scalar()
    if ctype and count == 0:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Content type {ctype} not implemented",
        )

    # Get secondary sorting clause
    sort_by, sort_order_fn = get_sorting_clause(sortby)

    stmt_query = _apply_common_filters(
        sa.select(cads_catalogue.database.Content), site, ctype
    ).order_by(
        sa.desc(cads_catalogue.database.Content.priority), sort_order_fn(sort_by)
    )

    results = session.scalars(stmt_query).all()
    return count, results


def query_content(
    session: sa.orm.Session,
    site: str,
    ctype: str,
    id: str,
):
    """Perform a database query for a single content."""
    stmt_query = _apply_common_filters(
        sa.select(cads_catalogue.database.Content), site, ctype
    ).where(
        cads_catalogue.database.Content.slug == id,
    )
    result = session.scalars(stmt_query).one()
    return result


def _build_content(content, request: fastapi.Request):
    related_datasets = content.resources

    return models.contents.Content(
        type=content.type,
        id=content.slug,
        title=content.title,
        description=content.description,
        links=[
            models.contents.Link(
                href=str(request.url_for("Get contents of type", ctype=content.type)),
                rel="parent",
                type="application/json",
            ),
            models.contents.Link(
                href=str(
                    request.url_for("Get content", ctype=content.type, id=content.slug)
                ),
                rel="self",
                type="application/json",
            ),
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
            *(
                models.contents.Link(
                    href=f'{request.url_for("Get Collections")}/{dataset.resource_uid}',
                    rel="related",
                    type="application/json",
                    title=dataset.title,
                )
                for dataset in related_datasets
            ),
        ],
        published=content.publication_date,
        updated=content.content_update,
        data=content.data,
    )


def _build_contents_response(results, request: fastapi.Request):
    return [_build_content(content, request=request) for content in results]


@router.get(
    "/",
    response_model=models.contents.Contents,
    response_model_exclude_none=True,
    name="Get contents",
)
def list_contents(
    request: fastapi.Request,
    sortby: extensions.ContentSortCriterion = extensions.ContentSortCriterion.title_asc,
    session=fastapi.Depends(dependencies.get_session),
    site=fastapi.Depends(dependencies.get_site),
) -> models.contents.Contents:
    """Endpoint to get all contents in the material catalogue."""
    count, results = query_contents(session, site=site, sortby=sortby)

    return models.contents.Contents(
        count=count,
        contents=_build_contents_response(
            results,
            request=request,
        ),
    )


@router.get(
    "/{ctype}",
    response_model=models.contents.Contents,
    response_model_exclude_none=True,
    name="Get contents of type",
)
def list_contents_of_type(
    request: fastapi.Request,
    ctype: str,
    sortby: extensions.ContentSortCriterion = extensions.ContentSortCriterion.title_asc,
    session=fastapi.Depends(dependencies.get_session),
    site=fastapi.Depends(dependencies.get_site),
) -> models.contents.Contents:
    """Endpoint to get all contents of a single type in the material catalogue."""
    count, results = query_contents(session, site=site, ctype=ctype, sortby=sortby)

    return models.contents.Contents(
        count=count,
        contents=_build_contents_response(
            results,
            request=request,
        ),
    )


@router.get(
    "/{ctype}/{id}",
    response_model=models.contents.Content,
    response_model_exclude_none=True,
    name="Get content",
)
def get_content(
    ctype: str,
    id: str,
    request: fastapi.Request,
    session=fastapi.Depends(dependencies.get_session),
    site=fastapi.Depends(dependencies.get_site),
) -> models.contents.Content:
    """Endpoint to get a content."""
    try:
        result = query_content(session, ctype=ctype, site=site, id=id)
    except sa.orm.exc.NoResultFound as exc:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Content {id} of type {ctype} not found",
        ) from exc
    return _build_content(result, request=request)
