import pyodbc
import pandas as pd
from datetime import datetime
from Model import Conn_DB
from Schemas import Representante as representante

class RepresentanteDAL:
    def __init__(self):
        self.conexao = Conn_DB.Conn()
        self.id_cliente = None
        self.nm_cliente = None
        self.dt_nascimento = None
        self.cpf = None
        self.rg = None
        self.telefone = None

    def _connect(self):
        return pyodbc.connect(self.conexao.str_conn)

    def retorna_clientes(self):
        query = """
        SELECT ID_CLIENTE AS ID,
               NM_CLIENTE AS Nome,
               CONVERT(DATE, DT_NASCIMENTO, 103) AS [Dt.Nascimento],
               CD_CPF AS CPF,
               CD_RG AS RG,
               NU_TELEFONE AS TELEFONE
        FROM TB_CLIENTES WITH(NOLOCK)
        """
        with self._connect() as conn:
            return pd.read_sql(query, conn)

    def retorna_representante_combo(self):
        query = """
        SELECT CONCAT(ID_REPRESENTANTE, ' - ', NM_CLIENTE) AS Representante
        FROM TB_REPRESENTANTES WITH(NOLOCK)
        ORDER BY ID_REPRESENTANTE
        """
        with self._connect() as conn:
            return pd.read_sql(query, conn)

    def inserir_representante(self,representante):
        query = f"""
        INSERT INTO TB_REPRESENTANTES (NM_CLIENTE, DT_NASCIMENTO, CD_CPF, CD_RG, NU_TELEFONE,NM_EMAIL)
        SELECT '{representante.nm_cliente}', CONVERT(DATE, '{representante.dt_nascimento}', 103), '{representante.cpf}', '{representante.rg}', '{representante.telefone}','{representante.email}'
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                return True
        except Exception:
            return False

    def retorna_representantes(self):
        query = """
        SELECT ID_REPRESENTANTE AS Id,
               NM_CLIENTE AS Cliente,
               DT_NASCIMENTO AS DtNascimento,
               CD_CPF AS CPF,
               CD_RG AS RG,
               NU_TELEFONE AS Telefone,
               NM_EMAIL AS Email
        FROM TB_REPRESENTANTES WITH(NOLOCK)
        """
        with self._connect() as conn:
            return pd.read_sql(query, conn)

    def verifica_cpf(self, cpf):
        query = f"""
        SELECT ISNULL(CD_CPF, '0') FROM TB_REPRESENTANTES WHERE CD_CPF = '{cpf}'
        """
        try:
            with self._connect() as conn:
                df = pd.read_sql(query, conn)
                return df.empty
        except Exception:
            return False

    def alterar_representante(self,representante):
        print("Aqui Alterar")
        query = f"""
        UPDATE TB_REPRESENTANTES
        SET NM_CLIENTE = '{representante.nm_cliente}',
            DT_NASCIMENTO = CONVERT(DATE, '{representante.dt_nascimento}', 103),
            CD_CPF = '{representante.cpf}',
            CD_RG = '{representante.rg}',
            NU_TELEFONE = '{representante.telefone}',
            NM_EMAIL = '{representante.email}'
        WHERE ID_REPRESENTANTE = {representante.id_cliente} 
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

def alterar_representante(self,representante):
        print("Aqui Alterar")
        query = f"""
        UPDATE TB_REPRESENTANTES
        SET NM_CLIENTE = '{representante.nm_cliente}',
            DT_NASCIMENTO = CONVERT(DATE, '{representante.dt_nascimento}', 103),
            CD_CPF = '{representante.cpf}',
            CD_RG = '{representante.rg}',
            NU_TELEFONE = '{representante.telefone}',
            NM_EMAIL = '{representante.email}'
        WHERE ID_REPRESENTANTE = {representante.id_cliente} 
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
