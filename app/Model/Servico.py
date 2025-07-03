import pyodbc
import pandas as pd
from datetime import datetime
from Model import Conn_DB
from Schemas import Servico as servico,ServicoCliente as servico_cliente

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

    def inserir_servico_cliente(self,servico_cliente):
        query = f""" 

        INSERT INTO TB_SERVICOS_CLIENTE(ID_CLIENTE" +
                    "                                                   ,ID_SERVICO" +
                    "                                                   ,VL_SERVICO" +
                    "                                                   ,VL_DESCONTO" +
                    "                                                   ,ID_USUARIO) " +
                    "SELECT " + {servico_cliente.id_cliente} +
                    "," {servico_cliente.id_servico}
                    ",convert(numeric(19,2),REPLACE('" + {servico_cliente.vl_servico} + "',',','.'))"+
                    ",convert(numeric(19,2),REPLACE('" + {servico_cliente.vl_desconto} + "',',','.'))" +
                    ","+{servico_cliente.id_usuario} """
        print(query)
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                return True
        except Exception:
            return False
        
    def retorna_servicos_cliente(self):
        query = """
        SELECT C.ID_CLIENTE                   AS ID
              ,C.NM_CLIENTE                 AS Cliente
              ,S.DS_SERVICO                 AS Serviço
              ,SC.DT_SERVICO                AS 'Data Inicio'
              ,SC.VL_SERVICO                AS Valor 
              ,SC.VL_DESCONTO               AS Desconto
              ,U.NM_USUARIO                 AS 'Usuário'
        FROM TB_CLIENTES         C WITH(NOLOCK)
        JOIN TB_SERVICOS_CLIENTE SC WITH(NOLOCK) ON SC.ID_CLIENTE = C.ID_CLIENTE
        JOIN TB_SERVICOS		   S WITH(NOLOCK) ON S.ID_SERVICO = SC.ID_SERVICO
        JOIN TB_USUARIOS         U WITH(NOLOCK) ON C.ID_USUARIO = SC.ID_USUARIO
        WHERE S.FL_RECORRENTE = 0  AND CONVERT(DATE,DT_SERVICO,103)=CONVERT(DATE,GETDATE(),103)
                                                  
        UNION
                                                  
        SELECT C.ID_CLIENTE       AS ID
              ,C.NM_CLIENTE             AS Cliente
              ,S.DS_SERVICO             AS Serviço
              ,SC.DT_SERVICO            AS 'Data Inicio'
              ,SC.VL_SERVICO            AS Valor 
              ,SC.VL_DESCONTO           AS Desconto
              ,U.NM_USUARIO                 AS 'Usuário'
        FROM TB_CLIENTES C WITH(NOLOCK)
        JOIN TB_SERVICOS_CLIENTE SC WITH(NOLOCK) ON SC.ID_CLIENTE = C.ID_CLIENTE
        JOIN TB_SERVICOS		 S WITH(NOLOCK) ON S.ID_SERVICO = SC.ID_SERVICO
        JOIN TB_USUARIOS         U WITH(NOLOCK) ON C.ID_USUARIO = SC.ID_USUARIO
        WHERE S.FL_RECORRENTE = 1   

        """
        with self._connect() as conn:
            return pd.read_sql(query, conn)
