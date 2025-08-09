import pyodbc
import pandas as pd
from Model.Conn_DB import Conn as Conn_DB
from Schemas import Cliente as cliente
from datetime import datetime


class Cliente:
    def __init__(self):
        self.conexao = Conn_DB()
        self.id_cliente = None
        self.nm_cliente = None
        self.dt_nascimento = None
        self.cpf = None
        self.rg = None
        self.telefone = None
        self.id_representante = None

    def _connect(self):
        return pyodbc.connect(self.conexao.str_conn)
 
    def retorna_clientes(self):
        query = """
            SELECT 
                C.ID_CLIENTE AS Id,
                C.NM_CLIENTE AS Nome,
                CONVERT(DATE, C.DT_NASCIMENTO, 103) AS DtNascimento,
                C.CD_CPF AS Cpf,
                C.CD_RG AS Rg,
                C.NU_TELEFONE AS Telefone,
                CONCAT(R.ID_REPRESENTANTE, ' - ', R.NM_CLIENTE) AS Representante
            FROM TB_CLIENTES C WITH(NOLOCK)
            LEFT JOIN TB_REPRESENTANTES R WITH(NOLOCK)
            ON R.ID_REPRESENTANTE = C.ID_REPRESENTANTE
        """
        try:
            with self._connect() as conn:
                return pd.read_sql(query, conn)
        except Exception as e:
            print("Erro ao buscar clientes:", e)
            return pd.DataFrame()

    def retorna_clientes_combo_box(self):
        query = """
            SELECT CONCAT(ID_CLIENTE, ' - ', NM_CLIENTE) AS Cliente
            FROM TB_CLIENTES WITH(NOLOCK)
            ORDER BY NM_CLIENTE
        """
        try:
            with self._connect() as conn:
                return pd.read_sql(query, conn)
        except Exception as e:
            print("Erro ao buscar clientes para combo box:", e)
            return pd.DataFrame()

    def inserir_cliente(self,cliente):
        print("Chegou aqui")
        query = f"""
            INSERT INTO TB_CLIENTES (
                NM_CLIENTE,
                DT_NASCIMENTO,
                CD_CPF,
                CD_RG,
                NU_TELEFONE,
                ID_REPRESENTANTE
            )
            SELECT 
                '{cliente.nm_cliente}',
                 CONVERT(DATE, '{cliente.dt_nascimento}', 103),
                '{cliente.cpf}',
                '{cliente.rg}',
                '{cliente.telefone}',
                {cliente.id_representante}
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                return True
        except Exception as e:
            print("Erro ao inserir cliente:", e)
            return False

    def alterar_cliente(self,cliente):
        query = f"""
            UPDATE TB_CLIENTES
            SET NM_CLIENTE = '{cliente.nm_cliente}',
                DT_NASCIMENTO = CONVERT(DATE, '{cliente.dt_nascimento}', 103),
                CD_CPF = '{cliente.cpf}',
                CD_RG = '{cliente.rg}',
                NU_TELEFONE = '{cliente.telefone}',
                ID_REPRESENTANTE = {cliente.id_representante}
            WHERE ID_CLIENTE = '{cliente.id_cliente}'
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                return True
        except Exception as e:
            print("Erro ao alterar cliente:", e)
            return False

    @property
    def str_conn(self):
        return self._str_conn