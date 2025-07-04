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
import sqlalchemy.dialects
import sqlalchemy.orm
import stac_fastapi.types
import stac_fastapi.types.core
import stac_pydantic

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


def get_sorting_clause(
    model: type[cads_catalogue.database.Resource], sort: str
) -> dict | tuple:
    """Get the sorting clause."""
    supported_sorts = {
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

    if sortby == "relevance" and q:
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


def get_extent(
    model: cads_catalogue.database.Resource,
) -> dict:
    """Get extent from model."""
    spatial = model.geo_extent or {}
    try:
        spatial_extent = stac_pydantic.collection.SpatialExtent(
            bbox=[
                [
                    spatial.get("bboxW", -180),
                    spatial.get("bboxS", -90),
                    spatial.get("bboxE", 180),
                    spatial.get("bboxN", 90),
                ]
            ],
        )
    except pydantic.ValidationError:
        spatial_extent = stac_pydantic.collection.SpatialExtent(
            bbox=[[-180, -90, 180, 90]]
        )
    begin_date = (
        f"{model.begin_date.isoformat()}T00:00:00Z" if model.begin_date else None
    )
    end_date = f"{model.end_date.isoformat()}T00:00:00Z" if model.end_date else None
    return stac_pydantic.collection.Extent(
        spatial=spatial_extent,
        temporal=stac_pydantic.collection.TimeInterval(
            interval=[[begin_date, end_date]],
        ),
    ).dict()


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
        collection_id=model.resource_uid, base_url=base_url
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
        additional_links += [
            {
                "rel": "license",
                "href": urllib.parse.urljoin(
                    config.settings.document_storage_url, license.download_filename
                ),
                "title": license.title,
            }
            for license in model.licences
        ]
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
                "title": "All messages related to the selected dataset",
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
            .options(*database.deferred_columns)
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
        return models.Message(
            id=message.message_uid,
            date=None,
            summary=message.summary,
            url=message.url,
            severity=message.severity,
            content=message.content,
            live=message.live,
        )
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
    """Transform database model to stac collection."""
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
    }

    if schema_org:
        schema_org_properties = {
            "creator_name": db_model.responsible_organisation,
            "creator_url": db_model.responsible_organisation_website,
            "creator_type": db_model.responsible_organisation_role,
            "creator_contact_email": db_model.contactemail,
            "file_format": db_model.file_format,
        }
        additional_properties.update(schema_org_properties)  # type: ignore

    return stac_fastapi.types.stac.Collection(
        type="Collection",
        id=db_model.resource_uid,
        stac_version="1.0.0",
        title=db_model.title,
        description=db_model.abstract,
        # FIXME: this is triggering a long list of subqueries
        keywords=(
            [keyword.keyword_name for keyword in db_model.keywords]
            if with_keywords
            else []
        ),
        # https://github.com/radiantearth/stac-spec/blob/master/collection-spec/collection-spec.md#license
        # note that this small check, even if correct, is triggering a lot of subrequests
        license=(
            "various" if not preview and len(db_model.licences) > 1 else "proprietary"
        ),
        extent=get_extent(db_model),
        links=collection_links,
        **additional_properties,
    )


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
        all_collections = [
            collection_serializer(
                collection, session=session, request=request, preview=True
            )
            for collection in query_results
        ]
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
    ) -> models.CADSCollections:
        """Read datasets from the catalogue."""
        portals = dependencies.get_portals_values(
            request.headers.get(config.PORTAL_HEADER_NAME)
        )

        route_ref = str(request.url_for(route_name))
        base_url = str(request.base_url)

        with self.reader.context_session() as session:
            search = session.query(self.collection_table).options(
                *database.deferred_columns
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

            serialized_collections = [
                collection_serializer(
                    collection, session=session, request=request, preview=True
                )
                for collection in collections
            ]

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

            collections = models.CADSCollections(
                collections=serialized_collections or [],
                links=links,
                numberMatched=count,
                numberReturned=len(serialized_collections),
            )

        if search_stats:
            with self.reader.context_session() as session:
                all_collections = self.load_catalogue(session, request, q, portals)

                search_utils.populate_facets(
                    all_collections=all_collections,
                    collections=collections,
                    keywords=kw,
                )

        return collections

    def all_collections(self, request: fastapi.Request) -> models.CADSCollections:
        """Read all collections from the catalogue."""
        return self.all_datasets(request=request)

    def get_collection(
        self, collection_id: str, request: fastapi.Request
    ) -> stac_fastapi.types.stac.Collection:
        """Get a STAC collection by id."""
        portals = dependencies.get_portals_values(
            request.headers.get(config.PORTAL_HEADER_NAME)
        )
        with self.reader.context_session() as session:
            collection = lookup_id(
                collection_id, self.collection_table, session, portals=portals
            )
            return collection_serializer(
                collection, session=session, request=request, preview=False
            )

    def get_item(self, **kwargs: dict[str, Any]) -> None:
        """Access to STAC items: explicitly not implemented."""
        raise exceptions.FeatureNotImplemented("STAC item is not implemented")

    def get_search(self, **kwargs: dict[str, Any]) -> None:
        """GET search catalog. Explicitly not implemented."""
        raise exceptions.FeatureNotImplemented("STAC search is not implemented")

    def item_collection(
        self, **kwargs: dict[str, Any]
    ) -> stac_fastapi.types.stac.ItemCollection:
        """Read an item collection from the database."""
        raise exceptions.FeatureNotImplemented("STAC items is not implemented")

    def post_search(self) -> None:
        """POST search catalog. Explicitly not implemented."""
        raise exceptions.FeatureNotImplemented("STAC search is not implemented")


cads_client = CatalogueClient()
