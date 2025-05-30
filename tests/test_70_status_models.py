import datetime

from cads_catalogue_api_service.models.status import CatalogueUpdateStatus


def test_transform_metadata_repo_commit_dict() -> None:
    """Test transform_metadata_repo_commit with dict input."""
    data = {
        "update_time": datetime.datetime.now(),
        "metadata_repo_commit": {"form1": "commit1", "form2": "commit2"},
    }
    catalogue_update = CatalogueUpdateStatus(**data)
    assert catalogue_update.forms_repo_commit == ["commit1", "commit2"]
    assert catalogue_update.catalogue_repo_commit is None
    assert catalogue_update.licence_repo_commit is None
    assert catalogue_update.message_repo_commit is None
    assert catalogue_update.cim_repo_commit is None
    assert catalogue_update.content_repo_commit is None


def test_transform_metadata_repo_commit_str() -> None:
    """Test transform_metadata_repo_commit with str input."""
    data = {
        "update_time": datetime.datetime.now(),
        "metadata_repo_commit": "commit1",
    }
    catalogue_update = CatalogueUpdateStatus(**data)
    assert catalogue_update.forms_repo_commit == ["commit1"]


def test_transform_metadata_repo_commit_none() -> None:
    """Test transform_metadata_repo_commit with None input."""
    data = {
        "update_time": datetime.datetime.now(),
        "metadata_repo_commit": None,
    }
    catalogue_update = CatalogueUpdateStatus(**data)
    assert catalogue_update.forms_repo_commit is None


def test_transform_metadata_repo_commit_empty_dict() -> None:
    """Test transform_metadata_repo_commit with empty dict input."""
    data = {
        "update_time": datetime.datetime.now(),
        "metadata_repo_commit": {},
    }
    catalogue_update = CatalogueUpdateStatus(**data)
    assert catalogue_update.forms_repo_commit is None


def test_transform_metadata_repo_commit_other_fields() -> None:
    """Test transform_metadata_repo_commit preserves other fields."""
    now = datetime.datetime.now()
    data = {
        "update_time": now,
        "catalogue_repo_commit": "cat_commit",
        "licence_repo_commit": "lic_commit",
        "message_repo_commit": "msg_commit",
        "cim_repo_commit": "cim_commit",
        "content_repo_commit": "content_commit",
        "metadata_repo_commit": "form_commit",
    }
    catalogue_update = CatalogueUpdateStatus(**data)
    assert catalogue_update.update_time == now
    assert catalogue_update.catalogue_repo_commit == "cat_commit"
    assert catalogue_update.licence_repo_commit == "lic_commit"
    assert catalogue_update.message_repo_commit == "msg_commit"
    assert catalogue_update.cim_repo_commit == "cim_commit"
    assert catalogue_update.content_repo_commit == "content_commit"
    assert catalogue_update.forms_repo_commit == ["form_commit"]


def test_transform_metadata_repo_commit_no_metadata_commit() -> None:
    """Test transform_metadata_repo_commit when metadata_repo_commit is not present."""
    now = datetime.datetime.now()
    data = {
        "update_time": now,
        "catalogue_repo_commit": "cat_commit",
    }
    catalogue_update = CatalogueUpdateStatus(**data)
    assert catalogue_update.update_time == now
    assert catalogue_update.catalogue_repo_commit == "cat_commit"
    assert catalogue_update.forms_repo_commit is None
