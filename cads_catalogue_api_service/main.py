# Copyright 2022, European Centre for Medium-Range Weather Forecasts (ECMWF).
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
from typing import Type

import attr
import fastapi
import fastapi.responses
import sqlalchemy.orm
import stac_fastapi.api.app
import stac_fastapi.extensions.core
import stac_fastapi.types
from cads_catalogue import database
from stac_pydantic.links import Relations
from stac_pydantic.shared import MimeTypes

from . import config, exceptions, serializers
from .session import Session

logger = logging.getLogger(__name__)


extensions = [
    # This extenstion is required, seems for a bad implementation
    stac_fastapi.extensions.core.TokenPaginationExtension(),
]


settings = config.SqlalchemySettings()


@attr.s
class CatalogueClient(stac_fastapi.types.core.BaseCoreClient):

    session: Session = attr.ib(default=Session.create_from_settings(settings))
    collection_table: Type[database.Resource] = attr.ib(default=database.Resource)
    collection_serializer: Type[serializers.Serializer] = attr.ib(
        default=serializers.CollectionSerializer
    )

    @staticmethod
    def _lookup_id(
        id: str, table: Type[database.BaseModel], session: sqlalchemy.orm.Session
    ) -> Type[database.BaseModel]:
        """Lookup row by id."""
        row = session.query(table).filter(table.id == id).first()
        if not row:
            raise stac_fastapi.types.errors.NotFoundError(
                f"{table.__name__} {id} not found"
            )
        return row

    def all_collections(self, **kwargs) -> stac_fastapi.types.stac.Collections:
        """Read all collections from the database."""
        base_url = str(kwargs["request"].base_url)
        with self.session.reader.context_session() as session:
            collections = session.query(self.collection_table).all()
            serialized_collections = [
                self.collection_serializer.db_to_stac(collection, base_url=base_url)
                for collection in collections
            ]
            links = [
                {
                    "rel": Relations.root.value,
                    "type": MimeTypes.json,
                    "href": base_url,
                },
                {
                    "rel": Relations.parent.value,
                    "type": MimeTypes.json,
                    "href": base_url,
                },
                {
                    "rel": Relations.self.value,
                    "type": MimeTypes.json,
                    "href": urllib.parse.urljoin(base_url, "collections"),
                },
            ]
            collection_list = stac_fastapi.types.stac.Collections(
                collections=serialized_collections or [], links=links
            )
            return collection_list

    def get_collection(
        self, collection_id: str, **kwargs
    ) -> stac_fastapi.types.stac.Collection:
        """Get collection by id."""
        base_url = str(kwargs["request"].base_url)
        with self.session.reader.context_session() as session:
            collection = self._lookup_id(collection_id, self.collection_table, session)
            return self.collection_serializer.db_to_stac(collection, base_url)

    def get_item(self, **kwargs) -> None:
        raise exceptions.FeatureNotImplemented("STAC item is not implemented")

    def get_search(
        self,
        **kwargs,
    ) -> None:
        """GET search catalog."""
        raise exceptions.FeatureNotImplemented("STAC search is not implemented")

    def item_collection(self, **kwargs) -> stac_fastapi.types.stac.ItemCollection:
        """Read an item collection from the database."""
        raise exceptions.FeatureNotImplemented("STAC items is not implemented")

    def post_search(self, **kwargs) -> None:
        raise exceptions.FeatureNotImplemented("STAC search is not implemented")


api = stac_fastapi.api.app.StacApi(
    settings=settings,
    extensions=extensions,
    client=CatalogueClient(),
    # search_get_request_model=create_get_request_model(extensions),
    # search_post_request_model=post_request_model,
)

app = api.app


@app.exception_handler(exceptions.FeatureNotImplemented)
async def unicorn_exception_handler(
    request: fastapi.Request, exc: exceptions.FeatureNotImplemented
):
    return fastapi.responses.JSONResponse(
        status_code=501,
        content={"message": exc.message},
    )
