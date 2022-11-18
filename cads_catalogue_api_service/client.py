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

import logging
import urllib
from typing import Any, Dict, List, Type

import attrs
import cads_catalogue.database
import fastapi
import fastapi_utils.session
import requests
import sqlalchemy.dialects
import sqlalchemy.orm
import stac_fastapi.types
import stac_fastapi.types.core
import stac_pydantic

from . import config, constrictor, exceptions, models

logger = logging.getLogger(__name__)


def get_sorting_clause(
    model: cads_catalogue.database.Resource, sort: str, inverse: bool
) -> dict:
    """Get the sorting clause."""
    supported_sorts = {
        "update": (
            model.record_update,
            sqlalchemy.desc if not inverse else sqlalchemy.asc,
        ),
        "title": (model.title, sqlalchemy.asc if not inverse else sqlalchemy.desc),
        "id": (model.resource_uid, sqlalchemy.asc if not inverse else sqlalchemy.desc),
    }
    return supported_sorts.get(sort) or supported_sorts["update"]


DEFINED_SORT_CRITERIA = {
    "update": ("__le__", "__gt__"),
    "title": ("__le__", "__gt__"),
    "id": ("__ge__", "__lt__"),
}


def lookup_dataset_by_id(
    id: str,
) -> List[str]:
    session_obj = cads_catalogue.database.ensure_session_obj(None)
    resource = cads_catalogue.database.Resource
    with session_obj() as session:
        query = session.query(resource)
        out = query.filter(resource.resource_uid == id).one()
    return out


def validate_constrains(
    collection_id: str, selection: Dict[str, List[str]]
) -> Dict[str, List[str]]:

    settings = config.Settings()
    storage_url = settings.document_storage_url
    dataset = lookup_dataset_by_id(collection_id)

    form_url = urllib.parse.urljoin(storage_url, dataset.form)
    raw_form = requests.get(form_url).json()
    form = constrictor.parse_form(raw_form)

    valid_combinations_url = urllib.parse.urljoin(storage_url, dataset.constraints)
    raw_valid_combinations = requests.get(valid_combinations_url).json()
    valid_combinations = constrictor.parse_valid_combinations(raw_valid_combinations)

    selection = constrictor.parse_selection(selection)

    return constrictor.apply_constraints(form, valid_combinations, selection)


def get_cursor_compare_criteria(sorting: str, back: bool = False) -> str:
    """Generate the proper cursor based on sorting criteria."""
    compare_criteria = DEFINED_SORT_CRITERIA.get(sorting)
    if not compare_criteria:
        return "__ge__" if not back else "__lt__"
    return compare_criteria[0 if not back else 1]


def apply_sorting(
    search: sqlalchemy.orm.Query,
    sorting: str,
    cursor: str,
    limit: int,
    inverse: bool = False,
):
    """Apply sorting to the running query.

    The sorting algorithm influences how pagination is build.
    Pagination is based on cursor: see https://use-the-index-luke.com/no-offset
    """
    sorting_clause = get_sorting_clause(
        cads_catalogue.database.Resource, sorting, inverse
    )
    sort_by, sort_order_fn = sorting_clause
    search = search.order_by(sort_order_fn(sort_by))

    get_cursor_direction = get_cursor_compare_criteria(sorting, inverse)

    # cursor meaning is based on the sorting criteria
    if cursor:
        sort_expr = getattr(sort_by, get_cursor_direction)(cursor)
        search = search.filter(*(sort_expr,))

    # limit is +1 for getting the next page
    search = search.limit(limit + 1)

    return search, sort_by


def apply_filters(search: sqlalchemy.orm.Query, q: str, kw: list):
    """Apply allowed search filters to the running query.

    Args
    ----
        search (sqlalchemy.orm.Query): current query
        q (str): search query (full text search)
        kw (list): list of keywords query
    """
    if q:
        search = search.filter(cads_catalogue.database.Resource.title.ilike(f"%{q}%"))
    if kw:
        search = search.filter(cads_catalogue.database.Resource.keywords.contains(kw))
    return search


def get_next_prev_links(
    collections: list,
    sort_by,
    cursor: str,
    limit: int,
    back: bool = False,
) -> dict[str, Any]:
    """Generate a prev/next links array.

    # See https://github.com/radiantearth/stac-api-spec/tree/main/item-search#pagination
    """
    links = {}

    if len(collections) <= limit:
        results = collections
    else:
        results = collections[:-1]

    # Next
    if len(collections) > limit or back:
        # We need a next link, as we have more records to explore
        next_cursor = cursor if back else getattr(collections[-1], sort_by.key)
        links["next"] = {"cursor": next_cursor}
    # Prev
    if cursor:
        # We have a cursor, so we provide a back link
        # NOTE: this is not perfect
        # The back link is always present because we don't know anything about the previous page
        back_cursor = getattr((results[0] if not back else results[-1]), sort_by.key)
        links["prev"] = {
            "cursor": back_cursor,
            "back": "true",
        }
    return links


def get_extent(
    model: cads_catalogue.database.Resource,
) -> stac_pydantic.collection.Extent:
    """Get extent from model."""
    spatial = model.geo_extent or {}
    begin_date = (
        f"{model.begin_date.isoformat()}T00:00:00Z" if model.begin_date else None
    )
    end_date = f"{model.end_date.isoformat()}T00:00:00Z" if model.end_date else None
    return stac_pydantic.collection.Extent(
        spatial=stac_pydantic.collection.SpatialExtent(
            bbox=[
                [
                    spatial.get("bboxW", -180),
                    spatial.get("bboxS", -90),
                    spatial.get("bboxN", 180),
                    spatial.get("bboxE", 90),
                ]
            ],
        ),
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


def get_reference(reference: dict[str, Any], base_url: str) -> dict[str, Any]:
    """Get the proper reference link data.

    We have multiple type of reference:

    - when "content" is provided (commonly for data for be show contextually)
    - when "url" is provided (for external resources)

    TODO: download_file not implemented yet.
    """
    response_reference = {
        "title": reference.get("title"),
    }
    if reference.get("content"):
        response_reference["rel"] = "reference"
        response_reference["href"] = urllib.parse.urljoin(
            base_url, reference["content"]
        )
    elif reference.get("url"):
        response_reference["rel"] = "external"
        response_reference["href"] = urllib.parse.urljoin(base_url, reference["url"])
    else:
        response_reference = None
        logger.error(f"Cannot obtain reference data for {reference}")
    return response_reference


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

    # Licenses
    additional_links = [
        {
            "rel": "license",
            "href": urllib.parse.urljoin(
                config.settings.document_storage_url, license.download_filename
            ),
            "title": license.title,
        }
        for license in model.licences
    ]

    if not preview:
        additional_links += [
            get_reference(reference, config.settings.document_storage_url)
            for reference in model.references
            if reference is not None
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
        additional_links.append(
            {
                "rel": "form",
                "href": urllib.parse.urljoin(
                    config.settings.document_storage_url, model.form
                ),
                "type": "application/json",
            }
        )

        # Constraints
        additional_links.append(
            {
                "rel": "constraints",
                "href": urllib.parse.urljoin(
                    config.settings.document_storage_url, model.constraints
                ),
                "type": "application/json",
            }
        )

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

        # Related datasets
        additional_links += [
            {
                "rel": "related",
                "href": f"{request.url_for(name='Get Collections')}/{related.resource_uid}",
                "title": related.title,
            }
            for related in model.related_resources
        ]

    collection_links += stac_fastapi.types.links.resolve_links(
        additional_links, base_url
    )
    return collection_links


def lookup_id(
    id: str,
    record: Type[cads_catalogue.database.Resource],
    session: sqlalchemy.orm.Session,
) -> cads_catalogue.database.Resource:
    """Lookup row by id."""
    try:
        row = session.query(record).filter(record.resource_uid == id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        raise stac_fastapi.types.errors.NotFoundError(
            f"{record.__name__} {id} not found"
        )
    return row


def collection_serializer(
    db_model: cads_catalogue.database.Resource,
    request: fastapi.Request,
    preview: bool = False,
) -> stac_fastapi.types.stac.Collection:
    """Transform database model to stac collection."""
    collection_links = generate_collection_links(
        model=db_model, request=request, preview=preview
    )

    assets = generate_assets(
        model=db_model, base_url=config.settings.document_storage_url
    )

    additional_properties = {
        **({"assets": assets} if assets else {}),
        **(
            {"tmp:publication_date": db_model.publication_date.strftime("%Y-%m-%d")}
            if db_model.publication_date
            else {}
        ),
        "tmp:doi": db_model.doi,
    }

    # properties not shown in preview mode
    full_view_propeties = (
        {}
        if preview
        else {
            "tmp:variables": db_model.variables,
            "tmp:description": db_model.description,
        }
    )

    return models.Dataset(
        type="Collection",
        id=db_model.resource_uid,
        stac_version="1.0.0",
        title=db_model.title,
        description=db_model.abstract,
        keywords=db_model.keywords,
        # https://github.com/radiantearth/stac-spec/blob/master/collection-spec/collection-spec.md#license
        license="various" if len(db_model.licences) > 1 else "proprietary",
        providers=db_model.providers or [],
        summaries=db_model.summaries or {},
        extent=get_extent(db_model),
        links=collection_links,
        **full_view_propeties,
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
    def reader(self) -> fastapi_utils.session.FastAPISessionMaker:
        """Return the reader for the catalogue database."""
        return fastapi_utils.session.FastAPISessionMaker(
            config.dbsettings.connection_string
        )

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
        return landing_page

    def conformance_classes(self) -> list[str]:
        """Generate conformance classes by adding extension conformance to base conformance classes.

        Also: remove conformance classes that are not implemented explicitly by the catalogue API.
        """
        # base_conformance_classes = self.base_conformance_classes.copy()
        STACConformanceClasses = stac_fastapi.types.conformance.STACConformanceClasses
        base_conformance_classes = [
            STACConformanceClasses.CORE,
            # TODO: implemented but not released yet
            # STACConformanceClasses.COLLECTIONS,
            "https://api.stacspec.org/v1.0.0-rc.1/collections",
        ]

        for extension in self.extensions:
            extension_classes = getattr(extension, "conformance_classes", [])
            base_conformance_classes.extend(extension_classes)

        return list(set(base_conformance_classes))

    def all_datasets(
        self,
        request: fastapi.Request,
        q: str = None,
        kw: list = [],
        sorting: str = "update",
        cursor: str = None,
        limit: int = 20,
        back: bool = False,
        route_name="Get Collections",
    ) -> stac_fastapi.types.stac.Collections:
        """Read datasets from the catalogue."""
        base_url = str(request.base_url)
        with self.reader.context_session() as session:
            search = session.query(self.collection_table)

            search = apply_filters(search, q, kw)
            search, sort_by = apply_sorting(
                search=search, sorting=sorting, cursor=cursor, limit=limit, inverse=back
            )

            collections = search.all()

            # Filter function always returns an item more than the limit to know if there is a next/prev page
            # But response is build or effective page size
            if len(collections) <= limit:
                results = collections
            else:
                results = collections[:-1]

            if len(results) == 0:
                raise stac_fastapi.types.errors.NotFoundError(
                    "Search does not match any dataset"
                )

            serialized_collections = [
                collection_serializer(collection, request=request, preview=True)
                for collection in (results if not back else reversed(results))
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
                    "href": request.url_for(name=route_name),
                },
            ]

            next_prev_links = get_next_prev_links(
                collections=collections,
                sort_by=sort_by,
                cursor=cursor,
                limit=limit,
                back=back,
            )
            if next_prev_links.get("next"):
                qs = urllib.parse.urlencode(
                    {
                        **{
                            k: v
                            for (k, v) in request.query_params.items()
                            if k != "back"
                        },
                        "cursor": next_prev_links["next"]["cursor"],
                    }
                )
                links.append(
                    {
                        "rel": "next",
                        "href": f"{request.url_for(name=route_name)}?{qs}",
                        "type": stac_pydantic.shared.MimeTypes.json,
                    }
                )
            if next_prev_links.get("prev"):
                qs = urllib.parse.urlencode(
                    {
                        **{k: v for (k, v) in request.query_params.items()},
                        "cursor": next_prev_links["prev"]["cursor"],
                        "back": "true",
                    }
                )
                links.append(
                    {
                        "rel": "prev",
                        "href": f"{request.url_for(name=route_name)}?{qs}",
                        "type": stac_pydantic.shared.MimeTypes.json,
                    }
                )

            collection_list = stac_fastapi.types.stac.Collections(
                collections=serialized_collections or [], links=links
            )
            return collection_list

    def all_collections(
        self, request: fastapi.Request
    ) -> stac_fastapi.types.stac.Collections:
        """Read all collections from the catalogue."""
        return self.all_datasets(request=request)

    def get_collection(
        self, collection_id: str, request: fastapi.Request
    ) -> stac_fastapi.types.stac.Collection:
        """Get a STAC collection by id."""
        with self.reader.context_session() as session:
            collection = lookup_id(collection_id, self.collection_table, session)
            return collection_serializer(collection, request=request, preview=False)

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
