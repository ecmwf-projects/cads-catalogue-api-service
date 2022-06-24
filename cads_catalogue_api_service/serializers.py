"""Serializers."""
import abc
from typing import Any

import attrs
import cads_catalogue.database
import stac_fastapi.types.links
import stac_fastapi.types.stac


@attrs.define
class Serializer(abc.ABC):
    """Defines serialization methods between the API and the data model."""

    @classmethod
    @abc.abstractmethod
    def db_to_stac(
        cls, db_model: cads_catalogue.database.BaseModel, base_url: str
    ) -> dict[str, Any]:
        """Transform database model to stac."""
        ...

    @classmethod
    @abc.abstractmethod
    def stac_to_db(cls, stac_data: dict[str, Any]) -> cads_catalogue.database.BaseModel:
        """Transform stac to database model."""
        ...

    @classmethod
    def row_to_dict(cls, db_model: cads_catalogue.database.BaseModel) -> dict[str, Any]:
        """Transform a database model to it's dictionary representation."""
        d = {}
        for column in db_model.__table__.columns:
            value = getattr(db_model, column.name)
            if value:
                d[column.name] = value
        return d


class CollectionSerializer(Serializer):
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

    @classmethod
    def stac_to_db(cls, stac_data: dict[str, Any]) -> cads_catalogue.database.Resource:
        """Transform stac collection to database model."""
        return cads_catalogue.database.Resource(**dict(stac_data))
