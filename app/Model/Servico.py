import pyodbc
import pandas as pd
from datetime import datetime
from Model import Conn_DB
from Schemas import Servico as servico

class ServicoDAL:
    def __init__(self):
        self.conexao = Conn_DB.Conn()
        self.id_servico = None
        self.ds_servico = None
        self.vl_servico = None
        self.fl_recorrente = None
        

    def _connect(self):
        return pyodbc.connect(self.conexao.str_conn)

    def retorna_servicos(self):
        query = """
        SELECT ID_SERVICO AS ID,
               DS_SERVICO AS Servico,
               VL_SERVICO AS Valor,
               FL_RECORRENTE AS Recorrente
        FROM TB_SERVICOS WITH(NOLOCK)
        """
        with self._connect() as conn:
            return pd.read_sql(query, conn)

    def retorna_servico_combo(self):
        query = """
        SELECT CONCAT(ID_SERVICO, ' - ', DS_SERVICO) AS Servico
        FROM TB_SERVICOS WITH(NOLOCK)
        ORDER BY ID_SERVICO
        """
        with self._connect() as conn:
            return pd.read_sql(query, conn)

    def inserir_servico(self,servico):
        query = f""" 
        INSERT INTO TB_SERVICOS (DS_SERVICO,VL_SERVICO,FL_RECORRENTE) 
        SELECT '{servico.ds_servico}',{servico.vl_servico},{servico.fl_recorrente}
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
   
    def alterar_servico(self,servico):
        query = f"""
        UPDATE TB_SERVICOS
         SET DS_SERVICO = '{servico.ds_servico}',
         VL_SERVICO = {servico.vl_servico},
         FL_RECORRENTE = {servico.fl_recorrente}
         WHERE ID_SERVICO = {servico.id_servico}
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
