# Copyright 2025, European Union.
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

import pytest

from cads_catalogue_api_service import middlewares


class MockRequest:
    def __init__(self, method="GET"):
        self.method = method


class MockResponse:
    def __init__(self, status_code=200):
        self.headers = {}
        self.status_code = status_code


def compute_call_next(status_code=200, headers=None):
    response = MockResponse(status_code=status_code)
    response.headers = headers or {}

    async def mock_call_next(request):
        return response

    return response, mock_call_next


@pytest.mark.asyncio
async def test_cache_middleware():
    """Test the CacheControlMiddleware class."""
    request = MockRequest()
    # Create an instance of CacheMiddleware
    middleware = middlewares.CacheControlMiddleware(app=None)
    response, call_next = compute_call_next()
    await middleware.dispatch(request, call_next)

    # Check that the response has the correct cache control header
    assert f"max-age={middlewares.CACHE_TIME}" in response.headers["cache-control"]
    assert (
        f" stale-while-revalidate={middlewares.CACHE_STALE_TIME}"
        in response.headers["cache-control"]
    )

    # Do not override/add cache headers if not a valid status code
    response, call_next = compute_call_next(status_code=500)
    await middleware.dispatch(request, call_next)

    # Do not override/add cache headers if not a valid req method
    request = MockRequest(method="POST")
    response, call_next = compute_call_next(status_code=500)
    await middleware.dispatch(request, call_next)

    assert "max-age" not in response.headers.get("cache-control", "")

    # Do not override/add cache headers if already present
    request = MockRequest()
    response, call_next = compute_call_next(
        headers={"cache-control": "no-cache,no-store"}
    )
    await middleware.dispatch(request, call_next)

    assert "max-age" not in response.headers.get("cache-control", "")
    assert response.headers.get("cache-control") == "no-cache,no-store"
