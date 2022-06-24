"""database session management."""
import contextlib
import logging
from typing import Iterator

import attrs
import fastapi_utils.session
import sqlalchemy
import stac_fastapi.types

from .config import SqlalchemySettings

logger = logging.getLogger(__name__)


class FastAPISessionMaker(fastapi_utils.session.FastAPISessionMaker):
    """FastAPISessionMaker."""

    @contextlib.contextmanager
    def context_session(self) -> Iterator[sqlalchemy.orm.Session]:
        """Override base method to include exception handling."""
        try:
            yield from self.get_db()
        except sqlalchemy.exc.StatementError as e:
            if isinstance(e.orig, sqlalchemy.exc.IntegrityError):
                raise stac_fastapi.types.errors.ForeignKeyError(
                    "collection does not exist"
                ) from e
            logger.error(e, exc_info=True)
            raise stac_fastapi.types.errors.DatabaseError("unhandled database error")


@attrs.define
class Session:
    """Database session management."""

    conn_string: str = attrs.field()
    reader: FastAPISessionMaker = attrs.field(init=False)

    @classmethod
    def create_from_settings(cls, settings: SqlalchemySettings) -> "Session":
        """Create a Session object from settings."""
        return cls(
            conn_string=settings.connection_string,
        )

    def __attrs_post_init__(self) -> None:
        """Post init handler."""
        self.reader = FastAPISessionMaker(self.conn_string)
