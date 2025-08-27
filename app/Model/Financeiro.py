import pyodbc
import pandas as pd
from datetime import datetime
from Model import Conn_DB
from Schemas import Financeiro as financeiro

class FinanceiroDAL:
    def __init__(self):
        self.conexao = Conn_DB.Conn()
    
    # Inserir pagamentos
    def inserir_debito(self, NmImposto, VlInicio, VlFim, VlPercentual):
        query = f"""
            INSERT INTO TB_IMPOSTOS (NM_IMPOSTO, VL_INICIO, VL_FIM, NUM_PERCENTUAL)
            SELECT ?, ?, ?, ?
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
        query = f"""
            WITH ULTIMO_CARGO AS (
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
        try:
            with pyodbc.connect(self.conn_str) as conn:
                cursor = conn.cursor()
                # Os 5 UNION usam @ID_USUARIO → passo 5 vezes o mesmo valor
                cursor.execute(query, (id_usuario, id_usuario, id_usuario, id_usuario, id_usuario))
                conn.commit()
            return True
        except Exception as e:
            print("Erro em insere_salarios_mes:", e)
            return False