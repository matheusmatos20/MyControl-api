import pyodbc
import pandas as pd

class Conn:
    def __init__(self):
        # self._str_conn = "DRIVER={SQL Server};SERVER=localhost;DATABASE=db_grantempo;Trusted_Connection=yes;"
        self._str_conn = (
            "DRIVER={SQL Server};"
            "SERVER=mfmatos_grantempo.sqlserver.dbaas.com.br;"
            "DATABASE=mfmatos_grantempo;"
            "UID=mfmatos_grantempo;"
            "PWD=gr@ntempo2024"
        )

    @property
    def str_conn(self):
        return self._str_conn 

    def _connect(self):
        return pyodbc.connect(self._str_conn)


        
    def get_usuario(self, username):
        query = f"""
        SELECT ID_USUARIO, NM_LOGIN, DS_SENHA
        FROM TB_USUARIOS WITH(NOLOCK)
        WHERE NM_LOGIN = '{username}'
        """
        print(query)
        with pyodbc.connect(self._str_conn) as conn:
            df = pd.read_sql(query, conn)
            if not df.empty:
                return df.iloc[0].to_dict()
            return None
