import pyodbc
import pandas as pd
import re
import calendar
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List
from Model import Conn_DB
from Schemas import Pagamento as pagamento
from Schemas import Parcelamento as parcelamento_schema
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
        print("Listar D?bitos")

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
        print("Listar D?bitos")

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
        descricao_base += f" | Emiss?o: {data_emissao.strftime('%d/%m/%Y')}"
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
                CONCAT('Vale Alimenta??o Colaborador: ', F.NM_FUNCIONARIO),
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
                    CONCAT('RESERVA - Parcela 13? Colaborador: ', F.NM_FUNCIONARIO),
                    1, CONVERT(NUMERIC(19,2), (CF.VL_SALARIO / 12)), 3,
                    CONVERT(VARCHAR(6), GETDATE(), 112)
                FROM TB_FUNCIONARIOS F
                JOIN ULTIMO_CARGO UC ON UC.ID_FUNCIONARIO = F.ID_FUNCIONARIO
                JOIN TB_CARGOS_FUNCIONARIOS CF ON CF.ID_CARGO_FUNCIONARIO = UC.ID_CARGO_FUNCIONARIO
            """










    @staticmethod
    def _parse_date(value):
        if value is None:
            raise ValueError('Data da primeira parcela ? obrigat?ria.')
        if isinstance(value, datetime):
            return value.date()
        text = str(value).strip()
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(text[:10], fmt).date()
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(text[:10]).date()
        except ValueError as exc:
            raise ValueError(f"Formato de data inv?lido: {value}") from exc

    @staticmethod
    def _add_months(base_date, months):
        year = base_date.year + (base_date.month - 1 + months) // 12
        month = ((base_date.month - 1 + months) % 12) + 1
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        day = min(base_date.day, last_day)
        return base_date.replace(year=year, month=month, day=day)

    def criar_parcelamento(self, parcelamento: parcelamento_schema.ParcelamentoCreateSchema):
        if parcelamento.numero_parcelas <= 0:
            raise ValueError("N?mero de parcelas deve ser maior que zero.")

        primeira_data = self._parse_date(parcelamento.data_primeira_parcela)
        if primeira_data is None:
            raise ValueError("Data da primeira parcela inv?lida.")

        valor_total = Decimal(str(parcelamento.valor_total))
        juros_percentual = Decimal(str(parcelamento.juros_percentual or 0))
        fator = Decimal('1.00') + (juros_percentual / Decimal('100'))
        total_com_juros = (valor_total * fator).quantize(Decimal('0.01'))
        valor_parcela_base = (total_com_juros / Decimal(parcelamento.numero_parcelas)).quantize(Decimal('0.01'))

        descricao = parcelamento.descricao.strip()
        if not descricao:
            raise ValueError('Descri??o do parcelamento ? obrigat?ria.')

        inseridos = 0
        with self._connect() as conn:
            cursor = conn.cursor()
            acumulado = Decimal('0.00')
            for numero in range(1, parcelamento.numero_parcelas + 1):
                vencimento = self._add_months(primeira_data, numero - 1)
                competencia = (vencimento.year * 100) + vencimento.month
                descricao_parcela = f"PARCELA {numero}/{parcelamento.numero_parcelas} - {descricao}"

                valor_parcela = valor_parcela_base
                if numero == parcelamento.numero_parcelas:
                    valor_parcela = (total_com_juros - acumulado).quantize(Decimal('0.01'))
                acumulado += valor_parcela

                cursor.execute("""
                    INSERT INTO TB_PAGAMENTOS
                        (ID_USUARIO, ID_FUNCIONARIO, DT_PAGAMENTO, DT_VENCIMENTO, DS_PAGAMENTO,
                         ID_FORNECEDOR, VL_PAGAMENTO, ID_FORMA_PAGAMENTO, COMPETENCIA)
                    VALUES (?, NULL, NULL, ?, ?, ?, ?, ?, ?)
                """,
                (
                    parcelamento.id_usuario,
                    vencimento,
                    descricao_parcela,
                    parcelamento.id_fornecedor,
                    float(valor_parcela),
                    parcelamento.id_forma_pagamento,
                    competencia,
                ))
                inseridos += 1

            conn.commit()

        return {
            "parcelas_criadas": inseridos,
            "valor_total_com_juros": float(total_com_juros)
        }

    def resumo_parcelas_semana(self) -> Dict[str, float]:
        query = """
            SELECT COUNT(*) AS Quantidade, COALESCE(SUM(VL_PAGAMENTO), 0) AS ValorTotal
            FROM TB_PAGAMENTOS WITH(NOLOCK)
            WHERE DS_PAGAMENTO LIKE 'PARCELA %'
              AND DT_PAGAMENTO IS NULL
              AND DT_VENCIMENTO BETWEEN CAST(GETDATE() AS DATE) AND DATEADD(DAY, 7, CAST(GETDATE() AS DATE))
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            row = cursor.fetchone()
            quantidade = int(row[0] or 0)
            valor = float(row[1] or 0)
            return {
                "quantidade": quantidade,
                "valor_total": round(valor, 2),
            }

    def listar_parcelas_semana(self) -> List[Dict[str, Any]]:
        query = """
            SELECT
                ID_PAGAMENTO,
                DS_PAGAMENTO,
                DT_VENCIMENTO,
                VL_PAGAMENTO
            FROM TB_PAGAMENTOS WITH(NOLOCK)
            WHERE DS_PAGAMENTO LIKE 'PARCELA %'
              AND DT_PAGAMENTO IS NULL
              AND DT_VENCIMENTO BETWEEN CAST(GETDATE() AS DATE) AND DATEADD(DAY, 7, CAST(GETDATE() AS DATE))
            ORDER BY DT_VENCIMENTO
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            rows = cursor.execute(query).fetchall()
            resultado: List[Dict[str, Any]] = []
            for row in rows:
                descricao = row.DS_PAGAMENTO or ''
                numero_parcela = None
                total_parcelas = None
                match = re.search(r"PARCELA (\d+)/(\d+)", descricao)
                if match:
                    numero_parcela = int(match.group(1))
                    total_parcelas = int(match.group(2))
                resultado.append(
                    {
                        "id_pagamento": row.ID_PAGAMENTO,
                        "descricao": descricao,
                        "data_vencimento": row.DT_VENCIMENTO.strftime("%Y-%m-%d") if row.DT_VENCIMENTO else None,
                        "valor": float(row.VL_PAGAMENTO or 0),
                        "numero_parcela": numero_parcela,
                        "total_parcelas": total_parcelas,
                    }
                )
            return resultado


