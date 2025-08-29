import datetime
from typing import Any

import pydantic


class CatalogueUpdateStatus(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    update_time: datetime.datetime
    catalogue_repo_commit: str | None = None
    forms_repo_commits: list[str] | None = None
    licence_repo_commit: str | None = None
    message_repo_commit: str | None = None
    cim_repo_commit: str | None = None
    content_repo_commit: str | None = None

    @pydantic.model_validator(mode="before")
    @classmethod
    def transform_metadata_repo_commit(cls, values: Any) -> dict[str, Any]:
        if isinstance(values, dict):
            output_values = {}
            for key, value in values.items():
                if key != "metadata_repo_commit":
                    output_values[key] = value

            metadata_commit = values.get("metadata_repo_commit")
            if isinstance(metadata_commit, dict) and metadata_commit:
                output_values["forms_repo_commits"] = list(metadata_commit.values())
            elif isinstance(metadata_commit, str):
                output_values["forms_repo_commits"] = [metadata_commit]
            else:
                output_values["forms_repo_commits"] = None
            return output_values
        return values
