import os
from typing import Any
from unittest.mock import Mock

import pytest
from cads_catalogue.database import Resource


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


@pytest.fixture(autouse=True)
def mock_hybrid_property():
    """Mock hybrid_property has_adaptor_costing."""

    def mock_instance_method(self):
        return True

    def mock_class_method(cls):
        from sqlalchemy import literal

        return literal(False)

    # create mock for hybrid_property
    mock_property = Mock()
    mock_property.__get__ = lambda self, instance, owner: (
        mock_instance_method(instance)
        if instance is not None
        else mock_class_method(owner)
    )

    Resource.has_adaptor_costing = mock_property
    yield
