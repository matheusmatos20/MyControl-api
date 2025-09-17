import pyodbc
import pandas as pd
from datetime import datetime
from Model import Conn_DB
from Schemas import Pagamento as pagamento
class PagamentoDAL:

    def __init__(self):
        self.conexao = Conn_DB.Conn()
        

    def _connect(self):
        return pyodbc.connect(self.conexao.str_conn)
    
    def listar_debitos(self):
        print("Listar Débitos")

        query = """select 
                            P.ID_PAGAMENTO as ID
                            ,CONCAT(P.ID_FORNECEDOR, ' - ',F.NM_FANTASIA) as Fornecedor
                            ,P.DS_PAGAMENTO as Descricao
                            ,FP.NM_FORMA_PAGAMENTO AS FormaPagamento
                            ,P.VL_PAGAMENTO as Valor
                            ,P.DT_VENCIMENTO as Vencimento
                            ,CASE WHEN DT_PAGAMENTO IS NULL
                            	  THEN 'Pendente' 
                            	  ELSE 'Pago'
                            	  END as StatusPagamento
                            FROM TB_PAGAMENTOS			P WITH(NOLOCK) 
                            INNER JOIN TB_FORMA_PAGAMENTOS FP WITH(NOLOCK) ON FP.ID = P.ID_FORMA_PAGAMENTO
                            INNER JOIN TB_FORNECEDORES	F WITH(NOLOCK) ON F.ID_FORNECEDOR = P.ID_FORNECEDOR

                
                """
        
        with self._connect() as conn:
            return pd.read_sql(query, conn)
        
    def listar_debitos_em_aberto(self):
        print("Listar Débitos")

        query = """select 
                    	P.ID_PAGAMENTO as ID
                    	,CONCAT(P.ID_FORNECEDOR, ' - ',F.NM_FANTASIA) as Fornecedor
                    	,P.DS_PAGAMENTO as Descricao
                    	,FP.NM_FORMA_PAGAMENTO AS FormaPagamento
                    	,P.VL_PAGAMENTO as Valor
                    	,P.DT_VENCIMENTO as Vencimento
                    	,CASE WHEN DATEDIFF(D , GETDATE(),P.DT_VENCIMENTO)<0
                    		  THEN 'Atrasado'
                    		  WHEN DATEDIFF(D , GETDATE(),P.DT_VENCIMENTO)=0
                    		  THEN 'Vence Hoje'
                    		  ELSE 'Pendente' END AS StatusPagamento

                    FROM TB_PAGAMENTOS				P WITH(NOLOCK) 
                    INNER JOIN TB_FORMA_PAGAMENTOS	FP WITH(NOLOCK) ON FP.ID = P.ID_FORMA_PAGAMENTO
                    INNER JOIN TB_FORNECEDORES		F WITH(NOLOCK) ON F.ID_FORNECEDOR = P.ID_FORNECEDOR
                    WHERE DT_PAGAMENTO IS NULL
                    ORDER BY P.DT_VENCIMENTO
                    """
        
        with self._connect() as conn:
            return pd.read_sql(query, conn)
        
    def baixar_pagamento(self, id_pagamento,id_usuario_baixa):
        
        query = f"""
            UPDATE TB_PAGAMENTOS 
            SET DT_PAGAMENTO = GETDATE()
                ,ID_USUARIO_BAIXA= {id_usuario_baixa}
           WHERE ID_PAGAMENTO = {id_pagamento}
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

    def delete_pagamento(self, idpagamento: int):
        
        query = f"""
           DELETE FROM TB_PAGAMENTOS 
           WHERE ID_PAGAMENTO = {idpagamento}
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

    def inserir_pagamento(self, pagamento):
        
        query = f"""
            INSERT INTO TB_PAGAMENTOS (
                ID_USUARIO,
                DT_PAGAMENTO,
                DT_VENCIMENTO,
                DS_PAGAMENTO,
                ID_FORNECEDOR,
                VL_PAGAMENTO,
                ID_FORMA_PAGAMENTO
            )
            SELECT
                {pagamento.id_usuario},
                CASE 
                    WHEN TRY_CONVERT(DATE, '{pagamento.dt_pagamento}', 103) IS NULL
                    THEN NULL 
                    ELSE CONVERT(DATE, '{pagamento.dt_pagamento}', 103)
                END,
                '{pagamento.dt_vencimento}', 
                '{pagamento.ds_pagamento}',
                {pagamento.id_fornecedor},
                REPLACE('{pagamento.vl_pagamento}', ',', '.'),
                {pagamento.id_forma_pagamento}
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

    def inserir_debito(self, NmImposto, VlInicio, VlFim, VlPercentual):
        query = """
            INSERT INTO TB_IMPOSTOS (NM_IMPOSTO, VL_INICIO, VL_FIM, NUM_PERCENTUAL)
            VALUES (?, ?, ?, ?)
        """
        try:
            with pyodbc.connect(self.conn_str) as conn:
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

    def insere_salarios_mes(self, id_usuario=1):
        query = """ WITH ULTIMO_CARGO AS (
                SELECT MAX(ID_CARGO_FUNCIONARIO) AS ID_CARGO_FUNCIONARIO, ID_FUNCIONARIO
                FROM TB_CARGOS_FUNCIONARIOS WITH(NOLOCK)
                GROUP BY ID_FUNCIONARIO
            )
            INSERT INTO TB_PAGAMENTOS
            (
                ID_USUARIO, ID_FUNCIONARIO, DT_PAGAMENTO, DT_VENCIMENTO, DS_PAGAMENTO,
                ID_FORNECEDOR, VL_PAGAMENTO, ID_FORMA_PAGAMENTO, COMPETENCIA
            )
            SELECT
                ?, F.ID_FUNCIONARIO, NULL,
                CONVERT(DATE, CONCAT(CONVERT(VARCHAR(6), GETDATE(), 112), '20'), 103),
                CONCAT('Adiantamento Colaborador: ', F.NM_FUNCIONARIO),
                1, CONVERT(NUMERIC(19,2), (CF.VL_SALARIO * 0.6)), 3,
                CONVERT(VARCHAR(6), GETDATE(), 112)
            FROM TB_FUNCIONARIOS F
            JOIN ULTIMO_CARGO UC ON UC.ID_FUNCIONARIO = F.ID_FUNCIONARIO
            JOIN TB_CARGOS_FUNCIONARIOS CF ON CF.ID_CARGO_FUNCIONARIO = UC.ID_CARGO_FUNCIONARIO

            UNION
            SELECT
                ?, F.ID_FUNCIONARIO, NULL,
                CONVERT(DATE, CONCAT(CONVERT(VARCHAR(6), DATEADD(MONTH, 1, GETDATE()), 112), '05'), 103),
                CONCAT('Pagamento Colaborador: ', F.NM_FUNCIONARIO),
                1, CONVERT(NUMERIC(19,2), (CF.VL_SALARIO * 0.4)), 3,
                CONVERT(VARCHAR(6), GETDATE(), 112)
            FROM TB_FUNCIONARIOS F
            JOIN ULTIMO_CARGO UC ON UC.ID_FUNCIONARIO = F.ID_FUNCIONARIO
            JOIN TB_CARGOS_FUNCIONARIOS CF ON CF.ID_CARGO_FUNCIONARIO = UC.ID_CARGO_FUNCIONARIO

            UNION
            SELECT
                ?, F.ID_FUNCIONARIO, NULL,
                CONVERT(DATE, CONCAT(CONVERT(VARCHAR(6), DATEADD(MONTH, 1, GETDATE()), 112), '05'), 103),
                CONCAT('Vale Transporte Colaborador: ', F.NM_FUNCIONARIO),
                1, VL_TRANSPORTE, 3,
                CONVERT(VARCHAR(6), GETDATE(), 112)
            FROM TB_FUNCIONARIOS F
            JOIN ULTIMO_CARGO UC ON UC.ID_FUNCIONARIO = F.ID_FUNCIONARIO
            JOIN TB_CARGOS_FUNCIONARIOS CF ON CF.ID_CARGO_FUNCIONARIO = UC.ID_CARGO_FUNCIONARIO
            WHERE VL_TRANSPORTE IS NOT NULL

            UNION
            SELECT
                ?, F.ID_FUNCIONARIO, NULL,
                CONVERT(DATE, CONCAT(CONVERT(VARCHAR(6), DATEADD(MONTH, 1, GETDATE()), 112), '05'), 103),
                CONCAT('Vale Alimentação Colaborador: ', F.NM_FUNCIONARIO),
                1, VL_ALIMENTACAO, 3,
                CONVERT(VARCHAR(6), GETDATE(), 112)
            FROM TB_FUNCIONARIOS F
            JOIN ULTIMO_CARGO UC ON UC.ID_FUNCIONARIO = F.ID_FUNCIONARIO
            JOIN TB_CARGOS_FUNCIONARIOS CF ON CF.ID_CARGO_FUNCIONARIO = UC.ID_CARGO_FUNCIONARIO
            WHERE VL_ALIMENTACAO IS NOT NULL

                UNION
                SELECT
                    ?, F.ID_FUNCIONARIO, NULL,
                    CONVERT(DATE, CONCAT(CONVERT(VARCHAR(6), DATEADD(MONTH, 1, GETDATE()), 112), '05'), 103),
                    CONCAT('RESERVA - Parcela 13º Colaborador: ', F.NM_FUNCIONARIO),
                    1, CONVERT(NUMERIC(19,2), (CF.VL_SALARIO / 12)), 3,
                    CONVERT(VARCHAR(6), GETDATE(), 112)
                FROM TB_FUNCIONARIOS F
                JOIN ULTIMO_CARGO UC ON UC.ID_FUNCIONARIO = F.ID_FUNCIONARIO
                JOIN TB_CARGOS_FUNCIONARIOS CF ON CF.ID_CARGO_FUNCIONARIO = UC.ID_CARGO_FUNCIONARIO
            """
