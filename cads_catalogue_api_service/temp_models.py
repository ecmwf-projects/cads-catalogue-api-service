"""SQLAlchemy ORM models."""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

metadata = sa.MetaData()
BaseModel = declarative_base(metadata=metadata)


class Collection(BaseModel):  # type:ignore
    """Collection ORM model."""

    __tablename__ = "collections"
    __table_args__ = {"schema": "catalogue"}

    id = sa.Column(sa.VARCHAR(1024), nullable=False, primary_key=True)
    stac_extensions = sa.Column(sa.ARRAY(sa.VARCHAR(300)), nullable=True)
    title = sa.Column(sa.VARCHAR(1024))
    description = sa.Column(sa.VARCHAR(1024), nullable=False)
    keywords = sa.Column(sa.ARRAY(sa.VARCHAR(300)))
    version = sa.Column(sa.VARCHAR(300))
    license = sa.Column(sa.VARCHAR(300), nullable=False)
    providers = sa.Column(JSONB)
    summaries = sa.Column(JSONB, nullable=True)
    extent = sa.Column(JSONB)
    links = sa.Column(JSONB)
    type = sa.Column(sa.VARCHAR(300), nullable=False)


if __name__ == "__main__":
    from sqlalchemy import create_engine

    from cads_catalogue_api_service.api import settings

    engine = create_engine(settings.connection_string)
    metadata.create_all(engine)
