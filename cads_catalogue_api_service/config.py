import typing as T

import stac_fastapi.types


class SqlalchemySettings(stac_fastapi.types.config.ApiSettings):
    """Postgres-specific API settings.

    Attributes:
        postgres_user: postgres username.
        postgres_password: postgres password.
        postgres_host: hostname for the connection.
        postgres_port: database port.
        postgres_dbname: database name.
    """

    postgres_user: str = "catalogue"
    postgres_password: str = "password"
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    postgres_dbname: str = "catalogue"

    # Fields which are defined by STAC but not included in the database model
    forbidden_fields: T.Set[str] = {"type"}

    # Fields which are item properties but indexed as distinct fields in the database model
    indexed_fields: T.Set[str] = {"datetime"}

    @property
    def connection_string(self):
        """Create reader psql connection string."""
        return (
            f"postgresql://{self.postgres_user}"
            f":{self.postgres_password}@{self.postgres_host}"
            f":{self.postgres_port}/{self.postgres_dbname}"
        )
