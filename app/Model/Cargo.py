import pyodbc
import pandas as pd
from datetime import datetime
from Model import Conn_DB
from Schemas import Cargo as cargo
 
class CargoDAL:
    def __init__(self):
        self.conexao = Conn_DB.Conn()
        self.id_cargo = None
        self.ds_cargo = None
        

    def _connect(self):
        return pyodbc.connect(self.conexao.str_conn)

    def retorna_cargos(self):
        query = """
        SELECT ID_CARGO AS ID,
               DS_CARGO AS Cargo
        FROM TB_CARGOS WITH(NOLOCK)
        """
        with self._connect() as conn:
            return pd.read_sql(query, conn)

    def retorna_cargo_combo(self):
        query = """
        SELECT CONCAT(ID_CARGO, ' - ', DS_CARGO) AS Cargo
        FROM TB_CARGOS WITH(NOLOCK)
        ORDER BY ID_CARGO
        """
        with self._connect() as conn:
            return pd.read_sql(query, conn)

    def inserir_cargo(self,cargo):
        query = f""" 
        INSERT INTO TB_CARGOS (DS_CARGO) 
        SELECT '{cargo.ds_cargo}'
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                return True
        except Exception:
            return False
   
    def alterar_cargo(self,cargo):
        query = f"""
        UPDATE TB_CARGOS
         SET DS_CARGO = '{cargo.ds_cargo}',
         WHERE ID_CARGO = {cargo.id_cargo}
        """
        print(query)
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                return True
        except Exception:
            return False
