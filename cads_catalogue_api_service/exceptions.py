"""Custom exceptions."""

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

from typing import Callable, Dict, Type

import fastapi
import stac_fastapi.api.errors
import starlette
import structlog

# See https://github.com/stac-utils/stac-fastapi/blob/6db83a9c05d200d43e83c19a585fcf7f0d9e6396/stac_fastapi/api/stac_fastapi/api/errors.py  # noqa: E501

logger = structlog.getLogger(__name__)


def exception_handler_factory(status_code: int) -> Callable:
    """Create a FastAPI exception handler for a particular status code.

    Args:
    ----
        status_code: HTTP status code.

    Returns
    -------
        callable: an exception handler.
    """

    def handler(request: fastapi.Request, exc: Exception):
        """I handle exceptions!!."""
        logger.error(exc, exc_info=True)
        return generate_exception_response(status_code=status_code, title=str(exc))

    return handler


def add_exception_handlers(
    app: fastapi.FastAPI, status_codes: Dict[Type[Exception], int]
) -> None:
    """Add exception handlers to the FastAPI application.

    Args:
    ----
        app: the FastAPI application.
        status_codes: mapping between exceptions and status codes.

    Returns
    -------
        None.
    """
    for exc, code in status_codes.items():
        app.add_exception_handler(exc, exception_handler_factory(code))

    def request_validation_exception_handler(
        request: fastapi.Request, exc: Exception
    ) -> fastapi.responses.JSONResponse:
        return generate_exception_response(
            title="submitted data is not valid",
            detail=str(exc),
            status_code=starlette.status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    app.add_exception_handler(
        fastapi.exceptions.RequestValidationError, request_validation_exception_handler
    )


# Monkey patching yet another STAC Fastapi wrapper that makes Fastapi to not work as expected
stac_fastapi.api.errors.add_exception_handlers = add_exception_handlers


# *** Custom exceptions ***


class FeatureNotImplemented(NotImplementedError):
    """Exception class to track STAC feature is not implemented yet."""

    def __init__(self, message: str = "This STAC feature is not implemented yet."):
        super().__init__(message)
        self.message = message


def generate_exception_response(
    title, detail=None, status_code=starlette.status.HTTP_500_INTERNAL_SERVER_ERROR
) -> fastapi.responses.JSONResponse:
    """Build standard JSON error response."""
    return fastapi.responses.JSONResponse(
        status_code=status_code,
        content={
            "title": title,
            **({"detail": detail} if detail else {}),
            "trace_id": structlog.contextvars.get_contextvars().get(
                "trace_id", "unset"
            ),
        },
    )
