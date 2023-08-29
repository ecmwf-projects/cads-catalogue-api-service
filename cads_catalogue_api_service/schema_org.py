"""schema.org module for Google Datasets compatibility."""

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


import cads_catalogue
import fastapi
import sqlalchemy as sa
import stac_fastapi.types
import stac_fastapi.types.core

from cads_catalogue_api_service.client import collection_serializer

from . import dependencies, models

TEMPLATE = {
    "@context": "https://schema.org/",
    "@type": "Dataset",
    "name": "NCDC Storm Events Database",
    "description": """Storm Data is provided by the National Weather
    Service (NWS) and contain statistics on...""",
    "url": "https://catalog.data.gov/dataset/ncdc-storm-events-database",
    "sameAs": "https://gis.ncdc.noaa.gov/geoportal/catalog/search/resource/details.page?id=gov.noaa.ncdc:C00510",
    "identifier": [
        "https://doi.org/10.1000/182",
        "https://identifiers.org/ark:/12345/fk1234",
    ],
    "keywords": [
        "ATMOSPHERE > ATMOSPHERIC PHENOMENA > CYCLONES",
        "ATMOSPHERE > ATMOSPHERIC PHENOMENA > DROUGHT",
        "ATMOSPHERE > ATMOSPHERIC PHENOMENA > FOG",
        "ATMOSPHERE > ATMOSPHERIC PHENOMENA > FREEZE",
    ],
    # For some datasets we have multiple licences, so we'll use the
    #  STAC way of reportimg them (AKA: "various")
    "license": "https://creativecommons.org/publicdomain/zero/1.0/",
    "isAccessibleForFree": True,
    "creator": {
        "@type": "Organization",
        "url": "https://climate.copernicus.eu",
        "name": "Copernicus Climate Change Service",
        "logo": "https://climate.copernicus.eu/themes/custom/ce/logo.svg",
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "customer service",
            "email": "copernicus-support@ecmwf.int",
            "url": "https://cds.climate.copernicus.eu/contact-us",
        },
    },
    "funder": {
        "@type": "Organization",
        "sameAs": "https://ror.org/00tgqzw13",
        "name": "National Weather Service",
    },
    "includedInDataCatalog": {"@type": "DataCatalog", "name": "data.gov"},
    "distribution": [
        {
            "@type": "DataDownload",
            "encodingFormat": "CSV",
            "contentUrl": "https://www.ncdc.noaa.gov/stormevents/ftp.jsp",
        },
        {
            "@type": "DataDownload",
            "encodingFormat": "XML",
            "contentUrl": "https://gis.ncdc.noaa.gov/all-records/catalog/search/resource/details.page?id=gov.noaa.ncdc:C00510",
        },
    ],
    "temporalCoverage": "1950-01-01/2013-12-18",
    "spatialCoverage": {
        "@type": "Place",
        "geo": {"@type": "GeoShape", "box": "18.0 -65.0 72.0 172.0"},
    },
    # "variableMeasured":
    # "dateModified":
    # "discussionUrl":
    # "abstract":
    # "thumbnail" o "thumbnailUrl":
    # "text": ???
}


ECMWF_TEMPLATE = {
    "@context": "http://schema.org/",
    "@type": "Dataset",
    "name": "Fire danger indices historical data from the Copernicus Emergency Management Service",
    "description": """This data set provides complete historical reconstruction of meteorological
    conditions favourable to the start, spread and sustainability of fires. The fire danger metrics
    provided are part of a vast dataset produced by the Copernicus Emergency Management Service for
    the European Forest Fire Information System (EFFIS). The European Forest Fire Information System
    incorporates the fire danger indices for three different models developed in Canada, United States
    and Australia. In this dataset the fire danger indices are calculated using weather forecast from
    historical simulations provided by ECMWF ERA5 reanalysis.
    ERA5 by combining  model data and  a vast set of quality controlled observations provides a  globally
    complete and consistent data-set and is regarded as a good proxy for observed atmospheric conditions.
    The selected data records in this data set are regularly extended with time as ERA5 forcing data become
     available.
    This dataset is produced by ECMWF in its role of the computational centre for fire danger forecast of
    the CEMS,  on behalf of the Joint Research Centre which is the managing entity of the service.""",
    "url": "https://cds.climate.copernicus.eu/cdsapp#!/dataset/cems-fire-historical-v1",
    "sameAs": "https://cds.climate.copernicus.eu/dataset/cems-fire-historical-v1",
    "license": "licence-to-use-copernicus-products",
    "keywords": ["PRODUCT TYPE >  REANALYSIS", "SPATIAL COVERAGE >  GLOBAL"],
    "creator": {
        "@type": "Organization",
        "url": "https://climate.copernicus.eu",
        "name": "Copernicus Climate Change Service",
        "logo": "https://climate.copernicus.eu/themes/custom/ce/logo.svg",
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "customer service",
            "email": "copernicus-support@ecmwf.int",
            "url": "https://cds.climate.copernicus.eu/contact-us",
        },
    },
    "distribution": [
        {
            "@type": "DataDownload",
            "encodingFormat": "NetCDF (interpolated grid only)  and GRIB2 (all grids)",
            "contentUrl": "https://cds.climate.copernicus.eu/cdsapp#!/dataset/cems-fire-historical-v1",
        }
    ],
    "temporalCoverage": "Daily",
}


router = fastapi.APIRouter(
    prefix="",
    tags=["messages"],
    responses={fastapi.status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


def query_collection(
    session: sa.orm.Session,
    collection_id: str,
    request: fastapi.Request,
) -> stac_fastapi.types.stac.Collection:
    return collection_serializer(
        session.query(cads_catalogue.database.Resource)
        .filter(cads_catalogue.database.Resource.resource_uid == collection_id)
        .one(),
        request=request,
        schema_org=True,
    )


def get_url_link(collection: stac_fastapi.types.stac.Collection, type: str) -> str:
    return (
        ([link for link in collection["links"] if link["rel"] == type][0]["href"])
        if any(link["rel"] == type for link in collection["links"])
        else None
    )


@router.get(
    "/collections/{collection_id}/schema.org",
    response_model=models.SchemaOrgDataset,
)
def schema_org_jsonId(
    collection_id: str,
    request: fastapi.Request,
    session=fastapi.Depends(dependencies.get_session),
) -> models.SchemaOrgDataset:
    """Endpoint to get the proper schema.org compatible definition for the dataset.

    See https://developers.google.com/search/docs/appearance/structured-data/dataset
    """
    collection = query_collection(session, collection_id, request)
    url, license, distribution = None, None, None
    if "links" in collection and collection["links"]:
        url = get_url_link(collection, "self")
        license = get_url_link(collection, "license")
        distribution = get_url_link(collection, "layout")
    temporal_coverage = (
        collection.get("extent", {}).get("temporal", {}).get("interval", [])
    )
    temporal_coverage = (
        list(filter(None, temporal_coverage[0])) if temporal_coverage else []
    )

    box = collection.get("extent", {}).get("spatial", {}).get("bbox", [])

    return models.SchemaOrgDataset(
        context="http://schema.org/",
        type="Dataset",
        name=collection["title"],
        description=collection.get("description", None),
        url=url,
        sameAs=url,
        identifier=[f"https://doi.org/{collection['sci:doi']}"]
        if "sci:doi" in collection
        else [],
        license=license,
        keywords=collection.get("keywords", []),
        is_accessible_for_free=True,
        creator=models.SchemaOrgOrganization(
            type=collection.get("creator_role", None),
            url=collection.get("creator_url", None),
            name=collection["creator_name"],
            logo="",
            contact_point=models.SchemaOrgContactPoint(
                type="",
                contactType="",
                email=collection.get("creator_contact_email", None),
                url="",
            ),
        ),
        distribution=[
            models.SchemaOrgDataDownload(
                encodingFormat="", contentUrl=f"{distribution}/download"
            )
            if distribution
            else ""
        ],
        temporalCoverage="/".join(temporal_coverage) if temporal_coverage else None,
        spatialCoverage=models.SchemaOrgPlace(
            type="",
            geo=models.SchemaOrgGeoShape(
                type="",
                box=box[0] if box else [],
            ),
        ),
        dateModified=collection.get("updated", None),
        thumbnailUrl=collection.get("assets", {})
        .get("thumbnail", {})
        .get("href", None),
    )
