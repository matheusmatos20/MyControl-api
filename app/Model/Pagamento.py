import pyodbc
import pandas as pd
import re
from datetime import datetime
from decimal import Decimal
from Model import Conn_DB
from Schemas import Pagamento as pagamento
class PagamentoDAL:

    def __init__(self):
        self.conexao = Conn_DB.Conn()

    def _connect(self):
        return pyodbc.connect(self.conexao.str_conn)

    @staticmethod
    def _normalize_cnpj(cnpj: str) -> str:
        if not cnpj:
            return ''
        return re.sub(r'\D', '', cnpj)

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
        query = """
           DELETE FROM TB_PAGAMENTOS 
           WHERE ID_PAGAMENTO = ?
        """

        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (idpagamento,))
                if cursor.rowcount == 0:
                    return False
                conn.commit()
                return True
        except Exception as e:
            print('Erro em delete_pagamento:', e)
            return False

    def obter_fornecedor_por_cnpj(self, cnpj: str):
        normalized = self._normalize_cnpj(cnpj)
        if not normalized:
            return None
        query = """
            SELECT ID_FORNECEDOR, NM_FANTASIA,
                   REPLACE(REPLACE(REPLACE(CD_CNPJ_CPF,'.',''),'/',''),'-','') AS CNPJ
            FROM TB_FORNECEDORES WITH(NOLOCK)
            WHERE REPLACE(REPLACE(REPLACE(CD_CNPJ_CPF,'.',''),'/',''),'-','') = ?
        """
        debug_query = query.replace("?", f"'{normalized}'")
        print("DEBUG SQL:", debug_query)
    
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (normalized,))
            row = cursor.fetchone()
            if not row:
                return None
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, row))

    def obter_empresa_por_cnpj(self, cnpj: str):
        normalized = self._normalize_cnpj(cnpj)
        if not normalized:
            return None
        queries = [
            """
            SELECT ID_EMPRESA, NM_FANTASIA,
                   REPLACE(REPLACE(REPLACE(NR_CNPJ,'.',''),'/',''),'-','') AS CNPJ
            FROM TB_EMPRESA WITH(NOLOCK)
            WHERE REPLACE(REPLACE(REPLACE(NR_CNPJ,'.',''),'/',''),'-','') = ?
            """,
            """
            SELECT ID_EMPRESA, NM_FANTASIA,
                   REPLACE(REPLACE(REPLACE(NR_CNPJ,'.',''),'/',''),'-','') AS CNPJ
            FROM TB_EMPRESA WITH(NOLOCK)
            WHERE REPLACE(REPLACE(REPLACE(NR_CNPJ,'.',''),'/',''),'-','') = ?
            """
        ]
        
    
        for query in queries:
            try:
                with self._connect() as conn:
                    cursor = conn.cursor()
                    debug_query = query.replace("?", f"'{normalized}'")
                    print("DEBUG SQL:", debug_query)
    
                    cursor.execute(query, (normalized,))
                    row = cursor.fetchone()
                    if row:
                        columns = [col[0] for col in cursor.description]
                        return dict(zip(columns, row))
            except pyodbc.ProgrammingError:
                continue
        return None

    def registrar_aviso_nf(self, *, id_usuario: int, fornecedor: dict, empresa: dict, valor: Decimal, data_emissao, data_vencimento, numero_nf: str, serie_nf: str, chave_nf: str | None = None, observacao: str | None = None):
        descricao_base = f"NF {numero_nf}/{serie_nf} - fornecedor {fornecedor.get('NM_FANTASIA') or fornecedor.get('CNPJ')}"
        descricao_base += f" | Emissão: {data_emissao.strftime('%d/%m/%Y')}"
        if observacao:
            descricao_base += f" - {observacao}"
        if empresa.get('NM_FANTASIA'):
            descricao_base += f" | Empresa: {empresa['NM_FANTASIA']}"
        if chave_nf:
            descricao_base += f" | Chave: {chave_nf}"

        query = """
            INSERT INTO TB_PAGAMENTOS (
                ID_USUARIO,
                DT_PAGAMENTO,
                DT_VENCIMENTO,
                DS_PAGAMENTO,
                ID_FORNECEDOR,
                VL_PAGAMENTO,
                ID_FORMA_PAGAMENTO
            )
            VALUES (?, NULL, ?, ?, ?, ?, ?)
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            print(id_usuario, data_vencimento.isoformat(), descricao_base, fornecedor['ID_FORNECEDOR'], float(valor), 1)
            cursor.execute(
                query,
                (
                    5,
                    data_vencimento.isoformat(),
                    descricao_base,
                    fornecedor['ID_FORNECEDOR'],
                    float(valor),
                    1
                )
            )
            conn.commit()
            return True

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










