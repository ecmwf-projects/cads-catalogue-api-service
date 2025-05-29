import datetime

import pydantic


class CatalogueUpdateStatus(pydantic.BaseModel):
    update_time: datetime.datetime
    catalogue_repo_commit: str | None
    metadata_repo_commit: dict | None
    licence_repo_commit: str | None
    message_repo_commit: str | None
    cim_repo_commit: str | None
    content_repo_commit: str | None

    class Config:
        orm_mode = True
