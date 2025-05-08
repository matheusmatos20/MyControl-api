import pyodbc
import pandas as pd
from datetime import datetime
from Conn_DB import Conn  # Assumindo que você tenha essa classe como no código anterior
from Session import Session  # Também assumindo estrutura parecida com a C#


class Pagamento:
    def __init__(self):
        self.conexao = Conn()
        self.ds_pagamento = None
        self.dt_pagamento = None
        self.dt_vencimento = None
        self.id_fornecedor = None
        self.vl_pagamento = None
        self.id_forma_pagamento = None

    def _connect(self):
        return pyodbc.connect(self.conexao.str_conn)

    def inserir_pagamento(self):
        usuario_id = Session.instance().id_usuario  # Adaptado para seguir padrão do C#

        dt_pagamento_str = (
            f"NULL" if self.dt_pagamento is None or self.dt_pagamento.year == 1
            else f"CONVERT(DATE, '{self.dt_pagamento.strftime('%d/%m/%Y')}', 103)"
        )

        query = f"""
        INSERT INTO [dbo].[TB_PAGAMENTOS] (
            ID_USUARIO,
            DT_PAGAMENTO,
            DT_VENCIMENTO,
            DS_PAGAMENTO,
            ID_FORNECEDOR,
            VL_PAGAMENTO,
            ID_FORMA_PAGAMENTO
        )
        SELECT 
            {usuario_id},
            {dt_pagamento_str},
            CONVERT(DATE, '{self.dt_vencimento.strftime('%d/%m/%Y')}', 103),
            '{self.ds_pagamento}',
            {self.id_fornecedor},
            REPLACE('{self.vl_pagamento}', ',', '.'),
            {self.id_forma_pagamento}
        """

        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                return True
        except Exception as e:
            print("Erro ao inserir pagamento:", e)
            return False

    def retorna_fornecedores(self):
        query = """
        SELECT CONCAT(ID_FORNECEDOR,' - ',NM_FANTASIA) AS Fornecedor
        FROM TB_FORNECEDORES WITH(NOLOCK)
        """
        try:
            with self._connect() as conn:
                return pd.read_sql(query, conn)
        except Exception as e:
            print("Erro ao buscar fornecedores:", e)
            return pd.DataFrame()

    def retorna_forma_pagamento(self):
        query = """
        SELECT CONCAT(ID, ' - ', NM_FORMA_PAGAMENTO) AS FormaPagamento
        FROM TB_FORMA_PAGAMENTOS WITH(NOLOCK)
        """
        try:
            with self._connect() as conn:
                return pd.read_sql(query, conn)
        except Exception as e:
            print("Erro ao buscar formas de pagamento:", e)
            return pd.DataFrame()
