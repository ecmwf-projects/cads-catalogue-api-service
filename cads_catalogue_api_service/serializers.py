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

import attrs
import cads_catalogue.database
import stac_fastapi.types.links
import stac_fastapi.types.stac


@attrs.define
class CollectionSerializer:
    """Serialization methods for STAC collections."""

    @classmethod
    def db_to_stac(
        cls, db_model: cads_catalogue.database.Resource, base_url: str
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
