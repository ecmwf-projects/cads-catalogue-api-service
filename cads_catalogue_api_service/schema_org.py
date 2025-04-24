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
# mypy: ignore-errors

import cads_catalogue
import fastapi
import sqlalchemy as sa
import stac_fastapi.types
import stac_fastapi.types.core

from cads_catalogue_api_service.client import collection_serializer

from . import dependencies, models

router = fastapi.APIRouter(
    prefix="",
    tags=["schema.org"],
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
        session=session,
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
    response_model=models.schema_org.Dataset,
    response_model_by_alias=True,
    response_model_exclude_none=True,
    include_in_schema=False,
)
def schema_org_json_ld(
    collection_id: str,
    request: fastapi.Request,
    session=fastapi.Depends(dependencies.get_session),
) -> models.schema_org.Dataset:
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


    return models.schema_org.Dataset(
        context="http://schema.org/",
        type="Dataset",
        name=collection["title"],
        description=collection.get("description", None),
        url=url,
        identifier=(
            [f"https://doi.org/{collection['sci:doi']}"]
            if "sci:doi" in collection
            else []
        ),
        license=license,
        keywords=collection.get("keywords", []),
        isAccessibleForFree=True,
        creator=models.schema_org.Organization(
            url=collection.get("creator_url", None),
            name=collection["creator_name"],
            contactPoint=models.schema_org.ContactPoint(
                contactType="User support",
                # FIXME: This is a problem with input data
                email=collection.get("creator_contact_email", None),
                url=collection.get("creator_contact_email", None),
            ),
        ),
        distribution=[
            (
                models.schema_org.DataDownload(
                    encodingFormat=collection.get("file_format")
                    # Sometimes the file_format is not defined on the input data
                    or "application/octet-stream",
                    contentUrl=f"{url}?tab=download",
                )
                if distribution
                else ""
            )
        ],
        temporalCoverage="/".join(temporal_coverage) if temporal_coverage else None,
        spatialCoverage=models.schema_org.Place(
            type="",
            geo=models.schema_org.GeoShape(
                type="",
                box=box[0] if box else [],
            ),
        ),
        datePublished=collection.get("published", None),
        dateModified=collection.get("updated", None),
        image=collection.get("assets", {}).get("thumbnail", {}).get("href", None),
        isPartOf=[{
            "@type": "DataCatalog",
            "@id": "https://cds.climate.copernicus.eu/datasets",
            "name": "Climate Data Store"
        }],
    )
