"""Middlewares."""

# Copyright 2023, European Union.
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

import os
import uuid

import fastapi
import starlette
import structlog


# See https://github.com/snok/asgi-correlation-id/blob/5a7be6337f3b33b84a00d03baae3da999bb722d5/asgi_correlation_id/middleware.py  # noqa: E501
class LoggerInitializationMiddleware:
    """
    Middleware that initializes the logger for each incoming request.

    ASGI middleware that initializes a unique trace ID for each incoming request
    and adds it to the response headers.
    The trace ID is also stored in a thread-local variable for logging purposes.

    Parameters
    ----------
        app (starlette.types.ASGIApp): The ASGI application to wrap.

    Usage:
        app = LoggerInitializationMiddleware(app)
    """

    def __init__(self, app: starlette.types.ASGIApp):
        self.app = app

    async def __call__(
        self,
        scope: starlette.types.Scope,
        receive: starlette.types.Receive,
        send: starlette.types.Send,
    ):
        """
        Compute trace ID for the incoming request and adds it to the response headers.

        Also clears any existing thread-local logging context and binds the trace ID to it.

        Parameters
        ----------
            scope (starlette.types.Scope): The ASGI scope of the incoming request.
            receive (starlette.types.Receive): The ASGI receive channel.
            send (starlette.types.Send): The ASGI send channel.

        Returns
        -------
            None.
        """
        structlog.contextvars.clear_contextvars()
        # request = fastapi.Request(scope, receive=receive)
        # trace_id = request.headers.get("X-Trace-ID", None)
        trace_id = str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(trace_id=trace_id)

        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        async def send_with_trace_id(message):
            if message["type"] == "http.response.start":
                headers = starlette.datastructures.MutableHeaders(scope=message)
                headers.append("X-Trace-Id", trace_id)

            await send(message)

        await self.app(scope, receive, send_with_trace_id)


CACHEABLE_HTTP_METHODS = ["GET", "HEAD"]
CACHE_TIME = os.getenv("CACHE_TIME", "180")
CACHE_STALE_TIME = os.getenv("CACHE_STALE_TIME", "60")


class CacheControlMiddleware(starlette.middleware.base.BaseHTTPMiddleware):
    """Set Cache-Control header for any GET and HEAD requests.

    If header is set already by route handler or other middleware, not set by it.
    """

    async def dispatch(
        self,
        request: fastapi.Request,
        call_next: starlette.middleware.base.RequestResponseEndpoint,
    ) -> fastapi.Response:
        response = await call_next(request)
        if (
            "cache-control" not in response.headers
            and request.method in CACHEABLE_HTTP_METHODS
            and response.status_code == fastapi.status.HTTP_200_OK
        ):
            response.headers.update(
                {
                    "cache-control": (
                        f"public, max-age={CACHE_TIME},"
                        f" stale-while-revalidate={CACHE_STALE_TIME}"
                    )
                }
            )
        return response
