"""Serializers."""
import abc
from typing import TypedDict

import attr
from stac_fastapi.types import stac as stac_types
from stac_fastapi.types.links import CollectionLinks, resolve_links

from . import temp_models as database


@attr.s  # type:ignore
class Serializer(abc.ABC):
    """Defines serialization methods between the API and the data model."""

    @classmethod
    @abc.abstractmethod
    def db_to_stac(cls, db_model: database.BaseModel, base_url: str) -> TypedDict:
        """Transform database model to stac."""
        ...

    @classmethod
    @abc.abstractmethod
    def stac_to_db(cls, stac_data: TypedDict) -> database.BaseModel:
        """Transform stac to database model."""
        ...

    @classmethod
    def row_to_dict(cls, db_model: database.BaseModel):
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
    def db_to_stac(cls, db_model: database.Collection, base_url: str) -> TypedDict:
        """Transform database model to stac collection."""
        collection_links = CollectionLinks(
            collection_id=db_model.id, base_url=base_url
        ).create_links()
        # We don't implements items. Let's remove the rel="items" entry
        collection_links = [link for link in collection_links if link["rel"] != "items"]

        db_links = db_model.links
        if db_links:
            collection_links += resolve_links(db_links, base_url)

        stac_extensions = db_model.stac_extensions or []

        return stac_types.Collection(
            type="Collection",
            id=db_model.id,
            stac_extensions=stac_extensions,
            stac_version="1.0.0",
            title=db_model.title,
            description=db_model.description,
            keywords=db_model.keywords,
            license=db_model.license,
            providers=db_model.providers,
            summaries=db_model.summaries,
            extent=db_model.extent,
            links=collection_links,
        )

    @classmethod
    def stac_to_db(cls, stac_data: TypedDict) -> database.Collection:
        """Transform stac collection to database model."""
        return database.Collection(**dict(stac_data))
