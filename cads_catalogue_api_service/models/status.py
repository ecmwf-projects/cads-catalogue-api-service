import datetime

import pydantic
from pydantic.utils import GetterDict


class CatalogueUpdateStatus(pydantic.BaseModel):
    update_time: datetime.datetime
    catalogue_repo_commit: str | None
    forms_repo_commits: list[str] | None
    licence_repo_commit: str | None
    message_repo_commit: str | None
    cim_repo_commit: str | None
    content_repo_commit: str | None

    @pydantic.root_validator(pre=True)
    def transform_metadata_repo_commit(cls, values: GetterDict | dict) -> dict:
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

    class Config:
        orm_mode = True
