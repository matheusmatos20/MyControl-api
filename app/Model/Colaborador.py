import pyodbc
import pandas as pd
from datetime import datetime
from Model import Conn_DB
from Schemas import Colaborador as colaborador

class ColaboradorDAL:
    def __init__(self):
        self.conexao = Conn_DB.Conn()
        self.id_servico = None
        self.ds_servico = None
        self.vl_servico = None
        self.fl_recorrente = None
        

    def _connect(self):
        return pyodbc.connect(self.conexao.str_conn)

    def retorna_colaborador(self):
        query = """
                SELECT ID_FUNCIONARIO 
                      ,NM_FUNCIONARIO
                      ,DT_NASCIMENTO
                      ,CD_CPF
                      ,CD_RG
                      ,ID_USUARIO
                FROM dbo.TB_FUNCIONARIOS WITH(NOLOCK)
        """
        with self._connect() as conn:
            return pd.read_sql(query, conn)

    def retorna_colaborador_combo(self):
        query = """
        SELECT CONCAT(ID_FUNCIONARIO, ' - ', NM_FUNCIONARIO) AS Colaborador
        FROM TB_FUNCIONARIOS WITH(NOLOCK)
        ORDER BY ID_FUNCIONARIO
        """
        with self._connect() as conn:
            return pd.read_sql(query, conn)

    def inserir_colaborador(self,colaborador):
        query = f""" 
                INSERT INTO [dbo].[TB_FUNCIONARIOS]
           ([NM_FUNCIONARIO]
           ,[DT_NASCIMENTO]
           ,[CD_CPF]
           ,[CD_RG]
           ,[ID_USUARIO]) 
     VALUES
           ('{colaborador.nm_funcionario}'
           ,'{colaborador.dt_nascimento}'
           ,'{colaborador.cd_cpf}'
           ,'{colaborador.cd_rg}'
           ,{colaborador.id_usuario}
        )"""
        print(query)
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                return True
        except Exception:
            return False
   
    def alterar_colaborador(self,colaborador):
        query = f"""
        UPDATE [dbo].[TB_FUNCIONARIOS]
        SET [NM_FUNCIONARIO] = '{colaborador.nm_funcionario}'
            ,[DT_NASCIMENTO] = '{colaborador.dt_nascimento}'
            ,[CD_CPF] = '{colaborador.cd_cpf}'
            ,[CD_RG] = '{colaborador.cd_rg}'
            ,[ID_USUARIO] = {colaborador.id_usuario}
        WHERE ID_FUNCIONARIO = {colaborador.id_funcionario}

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
