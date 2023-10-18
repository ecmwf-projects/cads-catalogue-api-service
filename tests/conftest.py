import os
from typing import Any

import pytest


@pytest.fixture(autouse=True)
def temp_environ() -> Any:
    """Create a modifiable environment that affect only the test scope."""
    old_environ = dict(os.environ)
    os.environ["CATALOGUE_DB_HOST"] = "dbhost"
    os.environ["CATALOGUE_DB_HOST_READ"] = "dbhostread"
    os.environ["CATALOGUE_DB_USER"] = "dbuser"
    os.environ["CATALOGUE_DB_PASSWORD"] = "password"
    os.environ["CATALOGUE_DB_NAME"] = "dbname"

    yield

    os.environ.clear()
    os.environ.update(old_environ)
