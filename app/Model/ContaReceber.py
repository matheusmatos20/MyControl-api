import calendar
import pyodbc
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List, Optional, Set, Tuple

from Model import Conn_DB


class ContaReceberDAL:
    def __init__(self):
        self.conexao = Conn_DB.Conn()

    def _connect(self):
        return pyodbc.connect(self.conexao.str_conn)

    def _parse_date(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        value = str(value).strip()
        if value.lower() in {"none", "null", ""}:
            return None
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                dt = datetime.strptime(value[:10], fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        try:
            dt = datetime.fromisoformat(value[:10])
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return value[:10]

    def _to_date(self, value: Any) -> Optional[date]:
        if value is None:
            return None
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        try:
            return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
        except ValueError:
            return None

    def _valor_liquido(self, bruto: Any, desconto: Any) -> float:
        valor_bruto = Decimal(str(bruto or 0))
        valor_desconto = Decimal(str(desconto or 0))
        liquido = (valor_bruto - valor_desconto).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return float(liquido)

    def _ajustar_dia(self, ano: int, mes: int, dia: Optional[int]) -> date:
        if not dia or dia <= 0:
            dia = 1
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        dia_ajustado = max(1, min(dia, ultimo_dia))
        return date(ano, mes, dia_ajustado)

    def _datas_recorrencia(self, referencia: date) -> Tuple[date, date]:
        mes_atual = referencia.month
        ano_atual = referencia.year
        prox_mes = mes_atual + 1
        prox_ano = ano_atual
        if prox_mes > 12:
            prox_mes = 1
            prox_ano += 1
        primeira = date(ano_atual, mes_atual, 1)
        segunda = date(prox_ano, prox_mes, 1)
        return primeira, segunda

    def _carregar_semana(self) -> List[Dict[str, Any]]:
        hoje = datetime.now().date()
        limite = hoje + timedelta(days=7)
        registros: List[Dict[str, Any]] = []
        existentes_combos: Set[Tuple[int, int, date]] = set()

        query_com_recebido = """
            SELECT
                SC.ID_SERVICO_CLIENTE,
                SC.ID_CLIENTE,
                SC.ID_SERVICO,
                C.NM_CLIENTE,
                S.DS_SERVICO,
                COALESCE(SC.VL_SERVICO, 0) AS VL_SERVICO,
                COALESCE(SC.VL_DESCONTO, 0) AS VL_DESCONTO,
                CAST(SC.DT_SERVICO AS DATE) AS DT_SERVICO,
                COALESCE(SC.VL_RECEBIDO, 0) AS VL_RECEBIDO
            FROM TB_SERVICOS_CLIENTE SC WITH(NOLOCK)
            INNER JOIN TB_CLIENTES C WITH(NOLOCK) ON C.ID_CLIENTE = SC.ID_CLIENTE
            INNER JOIN TB_SERVICOS S WITH(NOLOCK) ON S.ID_SERVICO = SC.ID_SERVICO
            WHERE (SC.DT_SERVICO IS NULL OR CAST(SC.DT_SERVICO AS DATE) BETWEEN ? AND ?)
        """

        query_sem_recebido = """
            SELECT
                SC.ID_SERVICO_CLIENTE,
                SC.ID_CLIENTE,
                SC.ID_SERVICO,
                C.NM_CLIENTE,
                S.DS_SERVICO,
                COALESCE(SC.VL_SERVICO, 0) AS VL_SERVICO,
                COALESCE(SC.VL_DESCONTO, 0) AS VL_DESCONTO,
                CAST(SC.DT_SERVICO AS DATE) AS DT_SERVICO
            FROM TB_SERVICOS_CLIENTE SC WITH(NOLOCK)
            INNER JOIN TB_CLIENTES C WITH(NOLOCK) ON C.ID_CLIENTE = SC.ID_CLIENTE
            INNER JOIN TB_SERVICOS S WITH(NOLOCK) ON S.ID_SERVICO = SC.ID_SERVICO
            WHERE (SC.DT_SERVICO IS NULL OR CAST(SC.DT_SERVICO AS DATE) BETWEEN ? AND ?)
        """

        contratos_query = """
            SELECT
                SC.ID_SERVICO_CLIENTE,
                SC.ID_CLIENTE,
                SC.ID_SERVICO,
                C.NM_CLIENTE,
                S.DS_SERVICO,
                COALESCE(SC.VL_SERVICO, 0) AS VL_SERVICO,
                COALESCE(SC.VL_DESCONTO, 0) AS VL_DESCONTO,
                COALESCE(NULLIF(SC.DIA_VENCIMENTO, 0), DAY(CAST(SC.DT_SERVICO AS DATE))) AS DIA_VENCIMENTO,
                CAST(SC.DT_SERVICO AS DATE) AS DT_INICIO,
                CAST(SC.DT_FIM AS DATE) AS DT_FIM
            FROM TB_SERVICOS_CLIENTE SC WITH(NOLOCK)
            INNER JOIN TB_CLIENTES C WITH(NOLOCK) ON C.ID_CLIENTE = SC.ID_CLIENTE
            INNER JOIN TB_SERVICOS S WITH(NOLOCK) ON S.ID_SERVICO = SC.ID_SERVICO
            WHERE S.FL_RECORRENTE = 1
              AND COALESCE(SC.FL_ATIVO, 1) = 1
        """
        contratos_query_basico = """

            SELECT

                SC.ID_SERVICO_CLIENTE,

                SC.ID_CLIENTE,

                SC.ID_SERVICO,

                C.NM_CLIENTE,

                S.DS_SERVICO,

                COALESCE(SC.VL_SERVICO, 0) AS VL_SERVICO,

                COALESCE(SC.VL_DESCONTO, 0) AS VL_DESCONTO,

                DAY(ISNULL(CAST(SC.DT_SERVICO AS DATE), CAST(GETDATE() AS DATE))) AS DIA_VENCIMENTO,

                CAST(SC.DT_SERVICO AS DATE) AS DT_INICIO,

                NULL AS DT_FIM

            FROM TB_SERVICOS_CLIENTE SC WITH(NOLOCK)

            INNER JOIN TB_CLIENTES C WITH(NOLOCK) ON C.ID_CLIENTE = SC.ID_CLIENTE

            INNER JOIN TB_SERVICOS S WITH(NOLOCK) ON S.ID_SERVICO = SC.ID_SERVICO

            WHERE S.FL_RECORRENTE = 1

        """



        with self._connect() as conn:
            cursor = conn.cursor()
            rows = []
            tem_coluna_recebido = True
            try:
                cursor.execute(query_com_recebido, hoje, limite)
                rows = cursor.fetchall()
            except pyodbc.ProgrammingError:
                tem_coluna_recebido = False
                cursor.execute(query_sem_recebido, hoje, limite)
                rows = cursor.fetchall()

            for row in rows:
                dt_prevista = self._to_date(row.DT_SERVICO) or hoje
                combo = (int(row.ID_CLIENTE), int(row.ID_SERVICO), dt_prevista)
                existentes_combos.add(combo)
                valor_previsto = self._valor_liquido(row.VL_SERVICO, row.VL_DESCONTO)
                valor_recebido = 0.0
                if tem_coluna_recebido:
                    valor_recebido = float(getattr(row, "VL_RECEBIDO", 0) or 0)
                registros.append(
                    {
                        "id": int(row.ID_SERVICO_CLIENTE),
                        "descricao": f"{row.NM_CLIENTE} - {row.DS_SERVICO}",
                        "data_prevista": dt_prevista.isoformat(),
                        "valor_previsto": valor_previsto,
                        "valor_recebido": valor_recebido,
                        "status": "Recebido" if valor_recebido >= valor_previsto and valor_previsto > 0 else "Registrado",
                    }
                )

            try:
                cursor.execute(contratos_query)
            except pyodbc.ProgrammingError:
                cursor.execute(contratos_query_basico)
            contratos = cursor.fetchall()
            referencias = self._datas_recorrencia(hoje)

            for contrato in contratos:
                dia_vencimento = contrato.DIA_VENCIMENTO or 1
                dt_inicio = self._to_date(contrato.DT_INICIO)
                dt_fim = self._to_date(contrato.DT_FIM)
                for referencia in referencias:
                    ano = referencia.year
                    mes = referencia.month
                    vencimento = self._ajustar_dia(ano, mes, dia_vencimento)
                    if vencimento < hoje or vencimento > limite:
                        continue
                    if dt_inicio and vencimento < dt_inicio:
                        continue
                    if dt_fim and vencimento > dt_fim:
                        continue
                    combo = (int(contrato.ID_CLIENTE), int(contrato.ID_SERVICO), vencimento)
                    if combo in existentes_combos:
                        continue
                    existentes_combos.add(combo)
                    valor_previsto = self._valor_liquido(contrato.VL_SERVICO, contrato.VL_DESCONTO)
                    registros.append(
                        {
                            "id": None,
                            "descricao": f"{contrato.NM_CLIENTE} - {contrato.DS_SERVICO}",
                            "data_prevista": vencimento.isoformat(),
                            "valor_previsto": valor_previsto,
                            "valor_recebido": 0.0,
                            "status": "Previsto",
                        }
                    )

        registros.sort(key=lambda item: item["data_prevista"] or "")
        return registros

    def resumo_semana(self) -> Dict[str, float]:
        registros = self._carregar_semana()
        total_previsto = sum(item.get("valor_previsto", 0.0) or 0.0 for item in registros)
        total_recebido = sum(item.get("valor_recebido", 0.0) or 0.0 for item in registros)
        saldo = total_previsto - total_recebido
        return {
            "total_previsto": round(total_previsto, 2),
            "total_recebido": round(total_recebido, 2),
            "saldo_em_aberto": round(saldo, 2),
        }

    def listar_contas_semana(self) -> List[Dict[str, Any]]:
        return self._carregar_semana()

    def resumo_servicos_recorrentes(self, competencia: Optional[int] = None) -> Dict[str, float]:
        if competencia is None:
            competencia = int(datetime.now().strftime("%Y%m"))
        ano = competencia // 100
        mes = competencia % 100
        if mes < 1 or mes > 12:
            raise ValueError("Competencia invalida")
        data_inicio = date(ano, mes, 1)
        data_fim = date(ano, mes, calendar.monthrange(ano, mes)[1])

        query = """
            SELECT
                COUNT(*) AS TotalServicos,
                COALESCE(SUM(SC.VL_SERVICO - COALESCE(SC.VL_DESCONTO, 0)), 0) AS ValorPrevisto
            FROM TB_SERVICOS_CLIENTE SC WITH(NOLOCK)
            INNER JOIN TB_SERVICOS S WITH(NOLOCK) ON S.ID_SERVICO = SC.ID_SERVICO
            WHERE S.FL_RECORRENTE = 1
              AND COALESCE(SC.FL_ATIVO, 1) = 1
              AND CAST(SC.DT_SERVICO AS DATE) <= ?
              AND (SC.DT_FIM IS NULL OR CAST(SC.DT_FIM AS DATE) >= ?)
        """
        query_basico = """
            SELECT
                COUNT(*) AS TotalServicos,
                COALESCE(SUM(SC.VL_SERVICO - COALESCE(SC.VL_DESCONTO, 0)), 0) AS ValorPrevisto
            FROM TB_SERVICOS_CLIENTE SC WITH(NOLOCK)
            INNER JOIN TB_SERVICOS S WITH(NOLOCK) ON S.ID_SERVICO = SC.ID_SERVICO
            WHERE S.FL_RECORRENTE = 1
              AND (SC.DT_SERVICO IS NULL OR CAST(SC.DT_SERVICO AS DATE) <= ?)
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, data_fim, data_inicio)
            except pyodbc.ProgrammingError:
                cursor.execute(query_basico, data_fim)
            row = cursor.fetchone()
            total_servicos = int(row[0] or 0)
            valor_previsto = float(row[1] or 0.0)
            return {
                "competencia": competencia,
                "servicos_ativos": total_servicos,
                "valor_previsto": round(valor_previsto, 2),
            }

    def gerar_lancamentos_recorrentes(self, competencia: Optional[int], id_usuario: int) -> int:
        if competencia is None:
            competencia = int(datetime.now().strftime("%Y%m"))
        ano = competencia // 100
        mes = competencia % 100
        if mes < 1 or mes > 12:
            raise ValueError("Competencia invalida")

        contratos_query = """
            SELECT
                SC.ID_SERVICO_CLIENTE,
                SC.ID_CLIENTE,
                SC.ID_SERVICO,
                COALESCE(SC.VL_SERVICO, 0) AS VL_SERVICO,
                COALESCE(SC.VL_DESCONTO, 0) AS VL_DESCONTO,
                COALESCE(NULLIF(SC.DIA_VENCIMENTO, 0), DAY(CAST(SC.DT_SERVICO AS DATE))) AS DIA_VENCIMENTO,
                CAST(SC.DT_SERVICO AS DATE) AS DT_INICIO,
                CAST(SC.DT_FIM AS DATE) AS DT_FIM
            FROM TB_SERVICOS_CLIENTE SC WITH(NOLOCK)
            INNER JOIN TB_SERVICOS S WITH(NOLOCK) ON S.ID_SERVICO = SC.ID_SERVICO
            WHERE S.FL_RECORRENTE = 1
              AND COALESCE(SC.FL_ATIVO, 1) = 1
        """

        existe_query = """
            SELECT COUNT(1)
            FROM TB_SERVICOS_CLIENTE SC WITH(NOLOCK)
            WHERE SC.ID_CLIENTE = ?
              AND SC.ID_SERVICO = ?
              AND CONVERT(INT, CONVERT(VARCHAR(6), SC.DT_SERVICO, 112)) = ?
        """

        insert_query = """
            INSERT INTO TB_SERVICOS_CLIENTE
                (ID_CLIENTE, ID_SERVICO, VL_SERVICO, VL_DESCONTO, ID_USUARIO, DT_SERVICO, FL_ATIVO, DIA_VENCIMENTO)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?)
        """

        update_query = """
            UPDATE TB_SERVICOS_CLIENTE
            SET ULTIMA_COMPETENCIA_GERADA = ?
            WHERE ID_SERVICO_CLIENTE = ?
        """

        inseridos = 0
        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(contratos_query)
            except pyodbc.ProgrammingError:
                # Colunas especificas de automacao nao existem; funcionalidade indisponivel
                return 0
            contratos = cursor.fetchall()
            for contrato in contratos:
                dia_vencimento = contrato.DIA_VENCIMENTO or 1
                vencimento = self._ajustar_dia(ano, mes, dia_vencimento)
                dt_inicio = self._to_date(contrato.DT_INICIO)
                dt_fim = self._to_date(contrato.DT_FIM)
                if dt_inicio and vencimento < dt_inicio:
                    continue
                if dt_fim and vencimento > dt_fim:
                    continue

                cursor.execute(
                    existe_query,
                    int(contrato.ID_CLIENTE),
                    int(contrato.ID_SERVICO),
                    competencia,
                )
                if cursor.fetchone()[0]:
                    continue

                cursor.execute(
                    insert_query,
                    (
                        int(contrato.ID_CLIENTE),
                        int(contrato.ID_SERVICO),
                        float(contrato.VL_SERVICO or 0),
                        float(contrato.VL_DESCONTO or 0),
                        id_usuario,
                        vencimento,
                        dia_vencimento,
                    ),
                )
                try:
                    cursor.execute(update_query, (competencia, int(contrato.ID_SERVICO_CLIENTE)))
                except pyodbc.ProgrammingError:
                    pass
                inseridos += 1

            conn.commit()
        return inseridos

    def finalizar_servico_recorrente(self, id_servico_cliente: int, dt_fim: Optional[str] = None) -> bool:
        data_formatada = self._parse_date(dt_fim)
        query = """
            UPDATE TB_SERVICOS_CLIENTE
            SET FL_ATIVO = 0,
                DT_FIM = COALESCE(?, CAST(GETDATE() AS DATE))
            WHERE ID_SERVICO_CLIENTE = ?
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (data_formatada, id_servico_cliente))
            affected = cursor.rowcount
            try:
                cursor.execute(
                    """
                        UPDATE TB_SERVICOS_CLIENTE
                        SET ULTIMA_COMPETENCIA_GERADA = NULL
                        WHERE ID_SERVICO_CLIENTE = ?
                    """,
                    (id_servico_cliente,),
                )
            except pyodbc.ProgrammingError:
                pass
            conn.commit()
            return affected > 0
