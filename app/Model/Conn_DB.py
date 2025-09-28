import os
import platform
import pyodbc
import pandas as pd


class Conn:
    _PREFERRED_DRIVERS = [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
        "ODBC Driver 13 for SQL Server",
        "SQL Server",
    ]

    def __init__(self):
        self._server = os.getenv("SQLSERVER_HOST", "mfmatos_grantempo.sqlserver.dbaas.com.br")
        self._database = os.getenv("SQLSERVER_DATABASE", "mfmatos_grantempo")
        self._user = os.getenv("SQLSERVER_USER", "mfmatos_grantempo")
        self._password = os.getenv("SQLSERVER_PASSWORD", "gr@ntempo2024")
        self._driver = self._resolve_driver()
        self._str_conn = self._build_connection_string(self._driver)

    @property
    def str_conn(self):
        return self._str_conn

    def _resolve_driver(self) -> str:
        forced_driver = os.getenv("SQLSERVER_ODBC_DRIVER")
        if forced_driver:
            return forced_driver

        available = {driver.strip() for driver in pyodbc.drivers()}
        for driver in self._PREFERRED_DRIVERS:
            if driver in available:
                return driver

        if not available and platform.system() == "Windows":
            return "SQL Server"
        if available:
            return sorted(available)[-1]

        # Default to the first preferred driver name so the error surfaced pelo pyodbc seja mais claro
        return self._PREFERRED_DRIVERS[0]

    def _build_connection_string(self, driver: str) -> str:
        parts = [
            f"DRIVER={{{driver}}}",
            f"SERVER={self._server}",
            f"DATABASE={self._database}",
            f"UID={self._user}",
            f"PWD={self._password}",
        ]
        if "ODBC Driver" in driver:
            parts.append("Encrypt=yes")
            parts.append("TrustServerCertificate=yes")
        return ";".join(parts)

    def _connect(self):
        try:
            return pyodbc.connect(self._str_conn)
        except pyodbc.Error as exc:
            raise RuntimeError(
                "Falha ao conectar ao SQL Server. Confira as variáveis de ambiente de conexão e se o driver ODBC está "
                "instalado no ambiente (ex.: msodbcsql18)."
            ) from exc

    def get_usuario(self, username):
        query = (
            """
        SELECT U.ID_USUARIO, U.NM_LOGIN, U.DS_SENHA, E.NM_FANTASIA AS EMPRESA
        FROM TB_USUARIOS U WITH(NOLOCK)
        INNER JOIN TB_EMPRESA E WITH(NOLOCK) ON E.ID_EMPRESA = U.ID_EMPRESA
        WHERE U.NM_LOGIN = ?
        """
        ).strip()

        with self._connect() as conn:
            df = pd.read_sql(query, conn, params=[username])
            if not df.empty:
                return df.iloc[0].to_dict()
            return None
