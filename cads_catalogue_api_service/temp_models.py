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
    license = sa.Column(sa.VARCHAR(300), nullable=False)
    providers = sa.Column(JSONB)
    summaries = sa.Column(JSONB, nullable=True)
    extent = sa.Column(JSONB)
    links = sa.Column(JSONB)
    # FIXME: why we need to store this in the db if it's always "Collection"?
    type = sa.Column(sa.VARCHAR(300), nullable=False)


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from cads_catalogue_api_service.main import settings

    engine = create_engine(settings.connection_string)
    Session = sessionmaker(bind=engine)
    metadata.create_all(engine)

    session = Session()
    era5 = Collection(
        id="reanalysis-era5-single-levels",
        stac_extensions=[
            "https://stac-extensions.github.io/item-assets/v1.0.0/schema.json"
        ],
        title="ERA5 hourly data on single levels from 1979 to present",
        description=(
            "ERA5 is the fifth generation ECMWF reanalysis for the global climate and weather "
            "for the past 4 to 7 decades. Currently data is available from 1950, split into "
            "Climate Data Store entries for 1950-1978 (preliminary back extension) and from "
            "1979 onwards (final release plus timely updates, this page). "
            "ERA5 replaces the ERA-Interim reanalysis."
        ),
        keywords=[
            "Variable domain: Atmosphere (surface)",
            "Variable domain: Atmosphere (upper air)",
            "Temporal coverage: Past",
            "Spatial coverage: Global",
            "Product type: Reanalysis",
            "Provider: Copernicus C3S",
        ],
        license="ECMWF-Copernicus-License-1.0",
        providers=[
            {
                "url": "https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5",
                "name": "ECMWF",
                "roles": ["producer", "licensor"],
            }
        ],
        extent={
            "spatial": {"bbox": [[-180.0, -90.0, 180.0, 90.0]]},
            "temporal": {
                "interval": [["1979-01-01T00:00:00Z", "2021-12-31T00:00:00Z"]]
            },
        },
        links=[
            {
                "rel": "license",
                "href": "https://cds.climate.copernicus.eu/cdsapp/#!/terms/licence-to-use-copernicus-products",  # noqa: E501
            },
            {
                "rel": "describedby",
                "href": "https://planetarycomputer.microsoft.com/dataset/reanalysis-era5-single-levels",  # noqa: E501
                "title": "Human readable dataset overview and reference",
                "type": "text/html",
            },
        ],
        type="Collection",
    )
    session.add(era5)
    session.commit()
