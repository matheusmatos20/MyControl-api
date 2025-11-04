import pyodbc
import pandas as pd
from datetime import datetime
from typing import Optional

from Model import Conn_DB
from Schemas import Financeiro as financeiro    


class FinanceiroDAL:
    def __init__(self):
        self.conexao = Conn_DB.Conn()

    def _connect(self):
        return pyodbc.connect(self.conexao.str_conn)

    # Inserir pagamentos
    def inserir_debito(self, NmImposto, VlInicio, VlFim, VlPercentual):
        query = """
            INSERT INTO TB_IMPOSTOS (NM_IMPOSTO, VL_INICIO, VL_FIM, NUM_PERCENTUAL)
            SELECT ?, ?, ?, ?
        """
        try:
            with pyodbc.connect(self.conexao.conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (NmImposto, VlInicio, VlFim, VlPercentual))
                conn.commit()
            return True
        except Exception as e:
            print("Erro em inserir_debito:", e)
            return False

    def retorna_fornecedores(self):
        query = """
            SELECT CONCAT(ID_FORNECEDOR,' - ',NM_FANTASIA) AS Fornecedor
            FROM TB_FORNECEDORES WITH(NOLOCK)
        """
        try:
            with pyodbc.connect(self.conn_str) as conn:
                df = pd.read_sql(query, conn)
            return df
        except Exception as e:
            print("Erro em retorna_fornecedores:", e)
            return pd.DataFrame()

    def insere_salarios_mes(self, competencia: Optional[int] = None, id_usuario: int = 1, id_forma_pagamento: int = 3) -> int:
        if competencia is None:
            competencia = int(datetime.now().strftime('%Y%m'))

        query = """
SET NOCOUNT ON;
DECLARE @competencia INT = ?;
DECLARE @usuario INT = ?;
DECLARE @forma INT = ?;
DECLARE @ano INT = @competencia / 100;
DECLARE @mes INT = @competencia % 100;

;WITH ultimo_cargo AS (
    SELECT *
    FROM (
        SELECT
            CF.*,
            ROW_NUMBER() OVER (PARTITION BY CF.ID_FUNCIONARIO ORDER BY CF.DT_CARGO DESC, CF.ID_CARGO_FUNCIONARIO DESC) AS Ordem
        FROM TB_CARGOS_FUNCIONARIOS CF WITH(NOLOCK)
          WHERE (CF.DT_DESLIGAMENTO IS NULL OR CF.DT_DESLIGAMENTO >= DATEFROMPARTS(@ano, @mes, 1))
    ) dados
    WHERE dados.Ordem = 1
)
INSERT INTO TB_PAGAMENTOS
    (ID_USUARIO, ID_FUNCIONARIO, DT_PAGAMENTO, DT_VENCIMENTO, DS_PAGAMENTO,
     ID_FORNECEDOR, VL_PAGAMENTO, ID_FORMA_PAGAMENTO, COMPETENCIA)
SELECT
    @usuario,
    UC.ID_FUNCIONARIO,
    NULL,
    CASE WHEN 5 > DAY(EOMONTH(DATEFROMPARTS(@ano, @mes, 1)))
         THEN EOMONTH(DATEFROMPARTS(@ano, @mes, 1))
         ELSE DATEFROMPARTS(@ano, @mes, 5)
    END,
    CONCAT('Folha ', RIGHT(CONCAT('0', @mes), 2), '/', @ano, ' - ', F.NM_FUNCIONARIO),
    1,
    UC.VL_CUSTO_TOTAL,
    @forma,
    @competencia
FROM ultimo_cargo UC
INNER JOIN TB_FUNCIONARIOS F WITH(NOLOCK) ON F.ID_FUNCIONARIO = UC.ID_FUNCIONARIO
WHERE NOT EXISTS (
    SELECT 1
    FROM TB_PAGAMENTOS P WITH(NOLOCK)
    WHERE P.ID_FUNCIONARIO = UC.ID_FUNCIONARIO
      AND P.COMPETENCIA = @competencia
      AND P.DS_PAGAMENTO LIKE 'Folha %'
);

DECLARE @rows INT = @@ROWCOUNT;
SELECT @rows AS Inseridos;
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (competencia, id_usuario, id_forma_pagamento))
            row = cursor.fetchone()
            inseridos = int(row[0] or 0)
            conn.commit()
            return inseridos

    def retorna_pagamentos(self, competencia=None, id_fornecedor=None, mostrar_futuros=False):
        params = []
        conditions = []
        competencia_int = None
        if competencia is not None:
            try:
                competencia_int = int(competencia)
            except (TypeError, ValueError):
                competencia_int = None
        if competencia_int is not None:
            conditions.append("CONVERT(INT, CONVERT(VARCHAR(6), P.DT_VENCIMENTO, 112)) = ?")
            params.append(competencia_int)
        elif mostrar_futuros:
            conditions.append("P.DT_VENCIMENTO >= CAST(GETDATE() AS DATE)")
        else:
            competencia_padrao = int(datetime.now().strftime('%Y%m'))
            conditions.append("CONVERT(INT, CONVERT(VARCHAR(6), P.DT_VENCIMENTO, 112)) = ?")
            params.append(competencia_padrao)
        if id_fornecedor is not None:
            conditions.append("P.ID_FORNECEDOR = ?")
            params.append(int(id_fornecedor))
        query = """
          select 
                    P.ID_PAGAMENTO								AS Id
                    ,CONVERT(INT,CONVERT(VARCHAR(6),P.DT_VENCIMENTO,112)) AS Competencia
                    ,P.DT_VENCIMENTO						AS DtVencimento
                    ,DS_PAGAMENTO							AS Descricao
                    ,F.NM_FANTASIA							AS Fornecedor
                    ,FP.NM_FORMA_PAGAMENTO					AS FormaPagamento
                    ,P.VL_PAGAMENTO							AS Valor
                    ,CASE WHEN(P.DT_PAGAMENTO IS NULL) 
                        THEN 'Pago'
                        ELSE 'Pendente'
                        END AS [Status]
          FROM TB_PAGAMENTOS		P  WITH(NOLOCK)
          LEFT JOIN TB_FORNECEDORES		F  WITH(NOLOCK) ON F.ID_FORNECEDOR = P.ID_FORNECEDOR
          LEFT JOIN TB_FORMA_PAGAMENTOS	FP WITH(NOLOCK) ON FP.ID = P.ID_FORMA_PAGAMENTO
        """
        if conditions:
            query += "\n          WHERE " + " AND ".join(conditions)
        query += "\n          ORDER BY P.DT_VENCIMENTO"
        try:
            with self._connect() as conn:
                df = pd.read_sql(query, conn, params=params)
                return df
        except Exception as e:
            print('Erro em retorna_pagamentos:', e)
        return pd.DataFrame()


    def retorna_creditos(self, competencia=None):
        competencia_int = competencia
        if competencia_int is None:
            competencia_int = int(datetime.now().strftime('%Y%m'))
        query = """
                 SELECT 
                        SC.ID_SERVICO_CLIENTE											 AS Id
                        ,CONVERT(INT,CONVERT(VARCHAR(6),SC.DT_SERVICO,112)) AS Competencia
                        ,SC.DT_SERVICO										 AS DtVencimento
                        ,S.DS_SERVICO											 AS Servico
                        ,C.NM_CLIENTE											 AS Cliente
                        --,FP.NM_FORMA_PAGAMENTO								 AS FormaPagamento
                        ,sc.VL_SERVICO										 AS Valor
                        ,sc.VL_DESCONTO									 AS Desconto
                        ,round((sc.VL_SERVICO - sc.VL_DESCONTO),2)			 AS VlLiquido
                        FROM TB_SERVICOS_CLIENTE					SC        WITH(NOLOCK)
                        LEFT JOIN TB_CLIENTES						   C        WITH(NOLOCK) ON C.ID_CLIENTE = SC.ID_CLIENTE
                        LEFT JOIN TB_SERVICOS						   S WITH(NOLOCK) ON S.ID_SERVICO = SC.ID_SERVICO
                        WHERE CONVERT(INT,CONVERT(VARCHAR(6),SC.DT_SERVICO,112)) = ?

                                """
        try:
            with self._connect() as conn:
                df = pd.read_sql(query, conn, params=[competencia_int])
                return df
        except Exception as e:
            print('Erro em retorna_creditos:', e)
        return pd.DataFrame()
