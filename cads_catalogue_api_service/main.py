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
from typing import Any, Type

import attrs
import cads_catalogue.database
import fastapi
import fastapi.openapi
import fastapi.responses
import sqlalchemy.orm
import stac_fastapi.api.app
import stac_fastapi.extensions.core
import stac_fastapi.types
import stac_fastapi.types.conformance
import stac_fastapi.types.links
import stac_pydantic

from . import config, exceptions
from .session import Session

logger = logging.getLogger(__name__)


extensions = [
    # This extenstion is required, seems for a bad implementation
    stac_fastapi.extensions.core.TokenPaginationExtension(),
]


settings = config.SqlalchemySettings()


@attrs.define
class CatalogueClient(stac_fastapi.types.core.BaseCoreClient):  # type: ignore

    session: Session = attrs.field(default=Session.create_from_settings(settings))
    collection_table: Type[cads_catalogue.database.Resource] = attrs.field(
        default=cads_catalogue.database.Resource
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

    @staticmethod
    def collection_serializer(
        db_model: cads_catalogue.database.Resource, base_url: str
    ) -> stac_fastapi.types.stac.Collection:
        """Transform database model to stac collection."""
        collection_links = stac_fastapi.types.links.CollectionLinks(
            collection_id=db_model.resource_id, base_url=base_url
        ).create_links()
        # We don't implement items. Let's remove the rel="items" entry
        collection_links = [link for link in collection_links if link["rel"] != "items"]

        db_links = db_model.links
        if db_links:
            collection_links += stac_fastapi.types.links.resolve_links(
                db_links, base_url
            )

        return stac_fastapi.types.stac.Collection(
            type="Collection",
            id=db_model.resource_id,
            stac_version="1.0.0",
            title=db_model.title,
            description=db_model.description,
            keywords=db_model.keywords,
            # license=db_model.licences,
            providers=db_model.providers,
            summaries=db_model.summaries,
            extent=db_model.extent,
            links=collection_links,
        )

    def conformance_classes(self) -> list[str]:
        """
        Generate conformance classes by adding extension conformance to base conformance classes.
        Also: remove concoformance classes that are not implemented explicitly by the catalogue API
        """
        # base_conformance_classes = self.base_conformance_classes.copy()
        STACConformanceClasses = stac_fastapi.types.conformance.STACConformanceClasses
        base_conformance_classes = [
            STACConformanceClasses.CORE,
            # FIXME: implemented but not released yet
            # STACConformanceClasses.COLLECTIONS,
            "https://api.stacspec.org/v1.0.0-rc.1/collections",
        ]

        for extension in self.extensions:
            extension_classes = getattr(extension, "conformance_classes", [])
            base_conformance_classes.extend(extension_classes)

        return list(set(base_conformance_classes))

    @staticmethod
    def _lookup_id(
        id: str,
        table: Type[cads_catalogue.database.BaseModel],
        session: sqlalchemy.orm.Session,
    ) -> Type[cads_catalogue.database.BaseModel]:
        """Lookup row by id."""
        row = session.query(table).filter(table.resource_id == id).first()
        if not row:
            raise stac_fastapi.types.errors.NotFoundError(
                f"{table.__name__} {id} not found"
            )
        return row

    def all_collections(
        self, request: fastapi.Request
    ) -> stac_fastapi.types.stac.Collections:
        """Read all collections from the database."""
        base_url = str(request.base_url)
        with self.session.reader.context_session() as session:
            collections = session.query(self.collection_table).all()
            serialized_collections = [
                self.collection_serializer(collection, base_url=base_url)
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
                    "href": urllib.parse.urljoin(base_url, "collections"),
                },
            ]
            collection_list = stac_fastapi.types.stac.Collections(
                collections=serialized_collections or [], links=links
            )
            return collection_list

    def get_collection(
        self, collection_id: str, request: fastapi.Request
    ) -> stac_fastapi.types.stac.Collection:
        """Get collection by id."""
        base_url = str(request.base_url)
        with self.session.reader.context_session() as session:
            collection = self._lookup_id(collection_id, self.collection_table, session)
            return self.collection_serializer(collection, base_url)

    def get_item(self, **kwargs: dict[str, Any]) -> None:
        raise exceptions.FeatureNotImplemented("STAC item is not implemented")

    def get_search(self, **kwargs: dict[str, Any]) -> None:
        """GET search catalog."""
        raise exceptions.FeatureNotImplemented("STAC search is not implemented")

    def item_collection(
        self, **kwargs: dict[str, Any]
    ) -> stac_fastapi.types.stac.ItemCollection:
        """Read an item collection from the database."""
        raise exceptions.FeatureNotImplemented("STAC items is not implemented")

    def post_search(self) -> None:
        raise exceptions.FeatureNotImplemented("STAC search is not implemented")


api = stac_fastapi.api.app.StacApi(
    settings=settings,
    extensions=extensions,
    client=CatalogueClient(),
)

app = api.app


def catalogue_openapi() -> dict[str, Any]:
    """OpenAPI, but with not implemented paths removed"""

    openapi_schema = fastapi.openapi.utils.get_openapi(
        title="CADS Catalogue", version=api.api_version, routes=api.app.routes
    )

    del openapi_schema["paths"]["/collections/{collection_id}/items"]
    del openapi_schema["paths"]["/collections/{collection_id}/items/{item_id}"]
    del openapi_schema["paths"]["/search"]

    api.app.openapi_schema = openapi_schema
    return openapi_schema


app.openapi = catalogue_openapi


@app.exception_handler(exceptions.FeatureNotImplemented)  # type: ignore
async def unicorn_exception_handler(
    request: fastapi.Request, exc: exceptions.FeatureNotImplemented
) -> fastapi.responses.JSONResponse:
    return fastapi.responses.JSONResponse(
        status_code=501,
        content={"message": exc.message},
    )
