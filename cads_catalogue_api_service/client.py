"""stac_fastapi client."""

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

import urllib
from typing import Any, Type

import attrs
import cads_catalogue
import fastapi
import pydantic
import sqlalchemy.orm
import stac_fastapi.types
import stac_fastapi.types.core
import stac_fastapi.types.links
import stac_fastapi.types.stac
import stac_pydantic
import structlog

from . import (
    config,
    database,
    dependencies,
    exceptions,
    extensions,
    models,
    sanity_check,
    search_utils,
)
from .fastapisessionmaker import FastAPISessionMaker

logger = structlog.getLogger(__name__)


def get_sorting_clause(
    model: type[cads_catalogue.database.Resource], sort: str
) -> dict | tuple:
    """Get the sorting clause."""
    supported_sorts = {
        "publication": (
            model.publication_date,
            sqlalchemy.desc,
        ),
        "update": (
            model.resource_update,
            sqlalchemy.desc,
        ),
        "title": (model.title, sqlalchemy.asc),
        "id": (model.resource_uid, sqlalchemy.asc),
    }
    return supported_sorts.get(sort) or supported_sorts["update"]


def apply_sorting_and_limit(
    search: sqlalchemy.orm.Query,
    sortby: str,
    page: int,
    limit: int,
    q: str | None = "",
):
    """Apply sortby and limit to the running query."""
    sorting_clause = get_sorting_clause(cads_catalogue.database.Resource, sortby)
    sort_by, sort_order_fn = sorting_clause

    if (
        sortby == "relevance"
        and q
        and config.settings.external_search_enabled
        and config.settings.external_search_endpoint
    ):
        # when using LLM search, sorting is already OK as it is returned by the apply_filters function
        pass
    elif sortby == "relevance" and q:
        # generate sorting by relevance based on input
        search = search.order_by(search_utils.fulltext_order_by(q))
    else:
        search = search.order_by(sort_order_fn(sort_by))

    search = search.offset(page * limit).limit(limit)

    return search


def get_next_prev_links(
    sortby: str,
    page: int,
    limit: int,
    count: int,
) -> dict[str, Any]:
    """Generate a prev/next links array.

    # See https://github.com/radiantearth/stac-api-spec/tree/main/item-search#pagination
    """
    links = {}

    # Next
    if page * limit + limit < count:
        # We need a next link, as we have more records to explore
        links["next"] = dict(page=page + 1, limit=limit, sortby=sortby)
    # Prev
    if page > 0:
        links["prev"] = dict(page=page - 1, limit=limit, sortby=sortby)
    return links


def generate_assets(
    model: cads_catalogue.database.Resource, base_url: str
) -> dict[str, dict[str, Any]]:
    """Generate STAC assets for collections."""
    assets = {}
    if model.previewimage:
        assets["thumbnail"] = {
            "href": urllib.parse.urljoin(base_url, model.previewimage),
            "type": "image/jpg",
            "roles": ["thumbnail"],
        }
    return assets


def generate_collection_links(
    model: cads_catalogue.database.Resource,
    request: fastapi.Request,
    preview: bool = False,
) -> list[dict[str, Any]]:
    """Generate collection links."""
    base_url = str(request.base_url)
    collection_links = stac_fastapi.types.links.CollectionLinks(
        collection_id=str(model.resource_uid), base_url=base_url
    ).create_links()
    # We don't implement items. Let's remove the rel="items" entry
    collection_links = [link for link in collection_links if link["rel"] != "items"]

    url_ref = request.url_for("Get Collections")

    # forced to typecheck here, due to https://github.com/python/mypy/issues/5382
    additional_links: list[dict[str, Any]] = []

    if model.qa_flag:
        additional_links.append(
            {
                "rel": "qa",
                # FIXME: a knowledge of webportal structure follows. Not optimal
                "href": f"/datasets/{model.resource_uid}?tab=quality_assurance_tab",
                "title": "Quality assessment of the dataset",
                "type": "text/html",
            }
        )

    if not preview:
        # Licenses
        for license in model.licences:
            href = (
                license.download_filename
                if license.spdx_identifier
                else urllib.parse.urljoin(
                    config.settings.document_storage_url, license.download_filename
                )
            )
            additional_links.append(
                {
                    "rel": "license",
                    "href": href,
                    "title": license.title,
                    "rev": license.revision,
                    "id": license.licence_uid,
                }
            )
        # Documentation
        additional_links += [
            {
                "rel": "describedby",
                "href": doc["url"],
                "title": doc.get("title"),
            }
            for doc in model.documentation
            if doc.get("url")
        ]

        # Form definition
        if model.form:
            # More an exception that normality, but we can have dataset with no form
            additional_links += [
                {
                    "rel": "form",
                    "href": urllib.parse.urljoin(
                        config.settings.document_storage_url, model.form
                    ),
                    "type": "application/json",
                }
            ]
        if model.constraints:
            additional_links += [
                {
                    "rel": "constraints",
                    "href": urllib.parse.urljoin(
                        config.settings.document_storage_url, model.constraints
                    ),
                    "type": "application/json",
                },
            ]

        # Retrieve process
        additional_links.append(
            {
                "rel": "retrieve",
                "href": urllib.parse.urljoin(
                    config.settings.processes_base_url,
                    f"processes/{model.resource_uid}",
                ),
                "type": "application/json",
            }
        )

        if model.has_adaptor_costing:
            additional_links.append(
                {
                    "rel": "costing_api",
                    "href": urllib.parse.urljoin(
                        config.settings.processes_base_url,
                        f"processes/{model.resource_uid}/costing",
                    ),
                    "type": "application/json",
                }
            )

        if model.layout:
            additional_links.append(
                {
                    "rel": "layout",
                    "href": urllib.parse.urljoin(
                        config.settings.document_storage_url, model.layout
                    ),
                    "type": "application/json",
                }
            )

        # Related datasets
        additional_links += [
            {
                "rel": "related",
                "href": f"{url_ref}/{related.resource_uid}",
                "title": related.title,
            }
            for related in model.related_resources
        ]

        # Messages related to dataset
        additional_links += [
            {
                "rel": "messages",
                "href": f"{url_ref}/{model.resource_uid}/messages",
                "title": f"All active messages on {model.title}",
            }
        ]

    collection_links += stac_fastapi.types.links.resolve_links(
        additional_links, base_url
    )
    return collection_links


def lookup_id(
    id: str,
    record: Type[cads_catalogue.database.Resource],
    session: sqlalchemy.orm.Session,
    portals: list[str] | None = None,
) -> cads_catalogue.database.Resource:
    """Lookup row by id."""
    try:
        search = (
            session.query(record)
            .options(
                *database.deferred_columns,
                sqlalchemy.orm.selectinload(record.licences),
            )
            .filter(record.resource_uid == id)
        )
        if portals:
            # avoid loading datasets from other portals, to block URL manipulation/pollution
            search = search.filter(record.portal.in_(portals))
        row = search.one()
    except sqlalchemy.orm.exc.NoResultFound as exc:
        raise stac_fastapi.types.errors.NotFoundError(
            f"{record.__name__} {id} not found"
        ) from exc
    return row


def get_active_message(
    db_model: cads_catalogue.database.Resource,
    session: sqlalchemy.orm.Session,
    filter_types=["warning", "critical"],
) -> models.Message | None:
    """Return the latest active message for a dataset."""
    message = (
        session.query(cads_catalogue.database.Message)
        .join(cads_catalogue.database.Message.resources)
        .where(
            cads_catalogue.database.Resource.resource_uid == db_model.resource_uid,
            cads_catalogue.database.Message.live.is_(True),
            cads_catalogue.database.Message.severity.in_(filter_types),
        )
        .order_by(cads_catalogue.database.Message.date.desc())
        .first()
    )
    if message:
        return models.Message.model_validate(message)
    return None


def collection_serializer(
    db_model: cads_catalogue.database.Resource,
    session: sqlalchemy.orm.Session,
    request: fastapi.Request,
    preview: bool = False,
    schema_org: bool = False,
    with_message: bool = True,
    with_keywords: bool = True,
) -> stac_fastapi.types.stac.Collection:
    """Transform database model to STAC collection."""
    collection_links = generate_collection_links(
        model=db_model, request=request, preview=preview
    )

    assets = generate_assets(
        model=db_model, base_url=config.settings.document_storage_url
    )

    active_message = get_active_message(db_model, session) if with_message else None
    processed_sanity_check = sanity_check.process(
        sanity_check.get_outputs(db_model.sanity_check)
    ).dict()

    additional_properties = {
        **({"assets": assets} if assets else {}),
        **(
            {"published": db_model.publication_date.isoformat() + "T00:00:00Z"}
            if db_model.publication_date
            else {}
        ),
        **(
            {"updated": db_model.resource_update.isoformat() + "T00:00:00Z"}
            if db_model.resource_update
            else {}
        ),
        # FIXME: this is not a 100% correct implementation of the STAC scientific extension.
        # One of the sci:xxx should be there, but CAMS dataset are not doing this
        **({"sci:doi": db_model.doi} if db_model.doi else {}),
        # *****************************************
        # *** CADS specific extension properties ***
        # *****************************************
        **({"cads:message": active_message} if active_message else {}),
        "cads:disabled_reason": db_model.disabled_reason,
        **({"cads:hidden": db_model.hidden} if db_model.hidden else {}),
        "cads:sanity_check": processed_sanity_check,
        **(
            {"cads:update_frequency": db_model.update_frequency}
            if db_model.update_frequency
            else {}
        ),
        **(
            {"cads:fair": db_model.fair_score}
            if db_model.fair_score is not None
            else {}
        ),
    }

    if schema_org:
        schema_org_properties = {
            "creator_name": db_model.responsible_organisation,
            "creator_url": db_model.responsible_organisation_website,
            "creator_type": db_model.responsible_organisation_role,
            "creator_contact_email": db_model.contactemail,
            "file_format": db_model.file_format,
            "keywords_urls": db_model.keywords_urls,
            "content_size": db_model.content_size,
        }
        additional_properties.update(schema_org_properties)  # type: ignore

    stac_license = "other"
    # https://github.com/radiantearth/stac-spec/blob/master/collection-spec/collection-spec.md#license
    # NOTE: this small check, even if correct, is triggering a lot of subrequests
    # FIXME: we can do the same we did for resource_data
    if (
        db_model.licences
        and len(db_model.licences) == 1
        and db_model.licences[0].spdx_identifier
    ):
        stac_license = db_model.licences[0].spdx_identifier

    collection_dict = {
        "type": "Collection",
        "id": db_model.resource_uid,
        "stac_version": "1.1.0",
        "title": db_model.title,
        "description": db_model.abstract,
        "summaries": {},
        "providers": (
            [{"name": db_model.ds_responsible_organisation}]
            if bool(db_model.ds_responsible_organisation)
            else []
        ),
        # NOTE: this is triggering a long list of subqueries
        # FIXME: we can do the same we did for resource_data
        "keywords": (
            [facet.facet_name for facet in db_model.facets] if with_keywords else []
        ),
        "license": stac_license,
        "extent": cads_catalogue.stac_helpers.get_extent(db_model),
        "links": collection_links,
        **additional_properties,
    }

    result = stac_fastapi.types.stac.Collection(**collection_dict)  # type: ignore
    return result


@attrs.define
class CatalogueClient(stac_fastapi.types.core.BaseCoreClient):
    """stac-fastapi custom client implementation for the CADS catalogue.

    This is based on cads-catalogue models, and redefines some STAC features that
    are not implemented.
    """

    collection_table: Type[cads_catalogue.database.Resource] = attrs.field(
        default=cads_catalogue.database.Resource
    )

    @property
    def reader(self) -> FastAPISessionMaker:
        """Return the reader session on the catalogue database."""
        session_maker = dependencies.get_sessionmaker(read_only=True)
        return session_maker

    def _landing_page(
        self,
        base_url: str,
        conformance_classes: list[str],
        extension_schemas: list[str],
    ) -> stac_fastapi.types.stac.LandingPage:
        landing_page = super()._landing_page(
            base_url, conformance_classes, extension_schemas
        )
        # removing link to search as it is not implemented
        landing_page["links"] = [
            link for link in landing_page["links"] if link["rel"] != "search"
        ]
        # FIXME: this must be different from site to site
        landing_page["id"] = "cds-stac-api"
        return landing_page

    def conformance_classes(self) -> list[str]:
        """Generate conformance classes by adding extension conformance to base conformance classes.

        Also: remove conformance classes that are not implemented explicitly by the catalogue API.
        """
        # base_conformance_classes = self.base_conformance_classes.copy()
        STACConformanceClasses = stac_fastapi.types.conformance.STACConformanceClasses
        base_conformance_classes = [
            STACConformanceClasses.CORE,
            STACConformanceClasses.COLLECTIONS,
            "https://github.com/stac-extensions/scientific/tree/v1.0.0",
            "https://github.com/stac-extensions/timestamps/tree/v1.1.0",
        ]

        for extension in self.extensions:
            extension_classes = getattr(extension, "conformance_classes", [])
            base_conformance_classes.extend(extension_classes)

        return list(set(base_conformance_classes))

    def load_catalogue(
        self, session: sqlalchemy.orm.Session, request, q, portals
    ) -> list:
        """Return the whole catalogue as a serialized structure."""
        query = session.query(self.collection_table).options(*database.deferred_columns)
        query_results = search_utils.apply_filters(
            session, query, q, kw=None, idx=None, portals=portals
        ).all()
        all_collections = []

        for collection in query_results:
            try:
                all_collections.append(
                    collection_serializer(
                        collection, session=session, request=request, preview=True
                    )
                )
            except pydantic.ValidationError as e:
                logger.error(
                    "Collection validation failed",
                    error=e,
                    id=collection.resource_uid,
                )
        return all_collections

    def all_datasets(
        self,
        request: fastapi.Request,
        q: str | None = None,
        kw: list[str] | None = [],
        idx: list[str] | None = [],
        sortby: extensions.CatalogueSortCriterion = extensions.CatalogueSortCriterion.update_desc,
        page: int = 0,
        limit: int = 999,
        route_name="Get Collections",
        search_stats: bool = False,
    ) -> stac_fastapi.types.stac.Collections | search_utils.CollectionsWithStats:
        """Read datasets from the catalogue."""
        portals = dependencies.get_portals_values(
            request.headers.get(config.PORTAL_HEADER_NAME)
        )

        route_ref = str(request.url_for(route_name))
        base_url = str(request.base_url)

        with self.reader.context_session() as session:
            search = session.query(self.collection_table).options(
                *database.deferred_columns,
                sqlalchemy.orm.selectinload(self.collection_table.licences),
            )
            search = search_utils.apply_filters(
                session, search, q, kw, idx, portals=portals
            )
            count = search.count()
            search = apply_sorting_and_limit(
                search=search, q=q, sortby=sortby, page=page, limit=limit
            )
            collections = search.all()

            if len(collections) == 0 and route_name != "Get Collections":
                # For canonical STAC requests to /collections, we don't want to raise a 404
                raise stac_fastapi.types.errors.NotFoundError(
                    "Search does not match any dataset"
                )

            serialized_collections = []
            for collection in collections:
                try:
                    serialized_collections.append(
                        collection_serializer(
                            collection, session=session, request=request, preview=True
                        )
                    )
                except pydantic.ValidationError as e:
                    logger.error(
                        "Collection validation failed",
                        error=e,
                        id=collection.resource_uid,
                    )

            links = [
                {
                    "rel": stac_pydantic.links.Relations.root.value,
                    "type": stac_pydantic.shared.MimeTypes.json,
                    "href": base_url,
                },
                {
                    "rel": stac_pydantic.links.Relations.parent.value,
                    "type": stac_pydantic.shared.MimeTypes.json,
                    "href": base_url,
                },
                {
                    "rel": stac_pydantic.links.Relations.self.value,
                    "type": stac_pydantic.shared.MimeTypes.json,
                    "href": route_ref,
                },
            ]

            next_prev_links = get_next_prev_links(
                sortby=sortby.value,
                page=page,
                limit=limit,
                count=count,
            )

            if next_prev_links.get("prev"):
                qs = urllib.parse.urlencode(
                    {
                        **{k: v for (k, v) in request.query_params.items()},
                        **next_prev_links["prev"],
                    }
                )
                links.append(
                    {
                        "rel": "prev",
                        "href": f"{route_ref}?{qs}",
                        "type": stac_pydantic.shared.MimeTypes.json,
                    }
                )
            if next_prev_links.get("next"):
                qs = urllib.parse.urlencode(
                    {
                        **{k: v for (k, v) in request.query_params.items()},
                        **next_prev_links["next"],
                    }
                )
                links.append(
                    {
                        "rel": "next",
                        "href": f"{route_ref}?{qs}",
                        "type": stac_pydantic.shared.MimeTypes.json,
                    }
                )

        if search_stats:
            collections = search_utils.CollectionsWithStats(
                collections=serialized_collections or [],
                links=links,
                numberMatched=count,
                numberReturned=len(serialized_collections),
                search={},
            )
            with self.reader.context_session() as session:
                all_collections = self.load_catalogue(session, request, q, portals)

                collections = search_utils.populate_facets(
                    all_collections=all_collections,
                    collections=collections,
                    keywords=kw,
                )
        else:
            collections = stac_fastapi.types.stac.Collections(
                collections=serialized_collections or [],
                links=links,
                numberMatched=count,
                numberReturned=len(serialized_collections),
            )

        return collections

    def all_collections(
        self,
        **kwargs: Any,
    ) -> stac_fastapi.types.stac.Collections:
        """Read all collections from the catalogue."""
        return self.all_datasets(**kwargs)

    def get_collection(
        self,
        collection_id: str,
        **kwargs: Any,
    ) -> stac_fastapi.types.stac.Collection:
        """Get a STAC collection by id."""
        request: fastapi.Request | None = kwargs.get("request")

        if request is None:
            raise ValueError("Request object is required but not provided")

        portals = dependencies.get_portals_values(
            request.headers.get(config.PORTAL_HEADER_NAME)
        )
        with self.reader.context_session() as session:
            collection = lookup_id(
                collection_id, self.collection_table, session, portals=portals
            )
            try:
                return collection_serializer(
                    collection, session=session, request=request, preview=False
                )
            except pydantic.ValidationError as e:
                logger.error(
                    "Collection validation failed",
                    error=e,
                    id=collection.resource_uid,
                )
                raise fastapi.HTTPException(
                    status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Collection validation failed",
                ) from e

    def get_item(
        self, item_id: str, collection_id: str, **kwargs: Any
    ) -> stac_fastapi.types.stac.Item:
        """Access to STAC items: explicitly not implemented."""
        raise exceptions.FeatureNotImplemented("STAC item is not implemented")

    def get_search(self, **kwargs: Any) -> None:  # type: ignore
        """GET search catalog. Explicitly not implemented."""
        raise exceptions.FeatureNotImplemented("STAC search is not implemented")

    def item_collection(self, **kwargs: Any) -> stac_fastapi.types.stac.ItemCollection:  # type: ignore
        """Read an item collection from the database."""
        raise exceptions.FeatureNotImplemented("STAC items is not implemented")

    def post_search(self) -> None:  # type: ignore
        """POST search catalog. Explicitly not implemented."""
        raise exceptions.FeatureNotImplemented("STAC search is not implemented")  # type: ignore


cads_client = CatalogueClient()
