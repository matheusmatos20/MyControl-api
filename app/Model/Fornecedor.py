import pyodbc
import pandas as pd
from datetime import datetime
from Model import Conn_DB
from Schemas import Fornecedor as fornecedor

class FornecedorDAL:
    def __init__(self):
        self.conexao = Conn_DB.Conn()
        self.id_fornecedor = None
        self.id_fornecedor=None
        self.nm_razao_social=None
        self.nm_fantasia=None
        self.cd_cnpj=None
        self.ds_endereco=None
        self.nu_telefone=None
        

    def _connect(self):
        return pyodbc.connect(self.conexao.str_conn)

    def retorna_fornecedores(self):
        query = """
        SELECT ID_FORNECEDOR AS id_fornecedor
              ,NM_RAZAO_SOCIAL  as nm_razao_social
              ,NM_FANTASIA as nm_fantasia
              ,CD_CNPJ_CPF as cd_cnpj
              ,DS_ENDERECO as ds_endereco
              ,NU_TELEFONE as nu_telefone
        FROM TB_FORNECEDORES WITH(NOLOCK)
        """
        with self._connect() as conn:
            return pd.read_sql(query, conn)

    def inserir_fornecedor(self,fornecedor):
        query = f""" 
       INSERT INTO TB_FORNECEDORES(
                                    NM_RAZAO_SOCIAL
                                    ,NM_FANTASIA
                                    ,CD_CNPJ_CPF
                                    ,DS_ENDERECO
                                    ,NU_TELEFONE
                                    )
        SELECT '{fornecedor.nm_razao_social}'
        ,'{fornecedor.nm_fantasia}'
        ,'{fornecedor.cd_cnpj}'
        ,'{fornecedor.ds_endereco}'
        ,'{fornecedor.nu_telefone}'
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
    def alterar_fornecedor(self, fornecedor):
        query = """
            UPDATE TB_FORNECEDORES
               SET NM_RAZAO_SOCIAL = ?,
                   NM_FANTASIA = ?,
                   CD_CNPJ_CPF = ?,
                   DS_ENDERECO = ?,
                   NU_TELEFONE = ?
             WHERE ID_FORNECEDOR = ?
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (
                    fornecedor.nm_razao_social,
                    fornecedor.nm_fantasia,
                    fornecedor.cd_cnpj,
                    fornecedor.ds_endereco,
                    fornecedor.nu_telefone,
                    fornecedor.id_fornecedor,
                ))
                if cursor.rowcount == 0:
                    return False
                conn.commit()
                return True
        except Exception as e:
            print('Erro em alterar_fornecedor:', e)
            return False


