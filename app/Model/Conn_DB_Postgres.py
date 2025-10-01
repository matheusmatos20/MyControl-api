import os
from typing import Any, Dict

import psycopg


class PostgresConn:
    """Helper for connecting to the AWS RDS PostgreSQL instance."""

    def __init__(self) -> None:
        self._host = os.getenv("PG_HOST", "db-mycontrol.crmf1jtelqlk.us-east-1.rds.amazonaws.com")
        self._port = int(os.getenv("PG_PORT", "5432"))
        self._database = os.getenv("PG_DATABASE", "db-mycontrol")
        self._user = os.getenv("PG_USER", "mycontroladmin")
        self._password = os.getenv("PG_PASSWORD", "MyControl&")
        self._sslmode = os.getenv("PG_SSLMODE", "require")
        self._options: Dict[str, Any] = {}

        application_name = os.getenv("PG_APP_NAME")
        if application_name:
            self._options["application_name"] = application_name

    def connect(self, **kwargs: Any) -> psycopg.Connection:
        """Return a new psycopg connection using environment or default values."""
        connection_kwargs: Dict[str, Any] = {
            "host": self._host,
            "port": self._port,
            "dbname": self._database,
            "user": self._user,
            "password": self._password,
            "sslmode": self._sslmode,
        }
        connection_kwargs.update(self._options)
        connection_kwargs.update(kwargs)
        return psycopg.connect(**connection_kwargs)

    def cursor(self, **kwargs: Any) -> psycopg.Cursor:
        """Convenience wrapper returning a cursor from a new connection."""
        return self.connect().cursor(**kwargs)
