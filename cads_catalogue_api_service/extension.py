from typing import Optional

import attr
from fastapi import FastAPI
from stac_fastapi.types.extension import ApiExtension


@attr.s
class CADSExtension(ApiExtension):
    """CADS STAC extension for datasets."""

    schema_href: Optional[str] = attr.ib(
        default="https://raw.githubusercontent.com/ecmwf-projects/cads-catalogue-api-service/main/schemas/cads-extension.json"  # noqa E501
    )

    def register(self, app: FastAPI) -> None:
        """Register the extension with a FastAPI application.

        Parameters
        ----------
        app: target FastAPI application.
        """
        pass
