import pyodbc
from datetime import datetime
from typing import Any, Dict, List, Optional

from Model import Conn_DB


class DespesaFixaDAL:
    def __init__(self):
        self.conexao = Conn_DB.Conn()

    def _connect(self):
        return pyodbc.connect(self.conexao.str_conn)

    def pendencias_resumo(self, competencia: Optional[int] = None) -> Dict[str, float]:
        if competencia is None:
            competencia = int(datetime.now().strftime("%Y%m"))
        query = """
            SELECT
                COUNT(*) AS Quantidade,
                COALESCE(SUM(VL_PREVISTO), 0) AS ValorPrevisto
            FROM TB_DESPESAS_FIXAS_LANCAMENTOS WITH(NOLOCK)
            WHERE COMPETENCIA = ?
              AND STATUS = 'AGUARDANDO'
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, competencia)
            row = cursor.fetchone()
            quantidade = int(row[0] or 0)
            valor = float(row[1] or 0)
            return {
                "competencia": competencia,
                "quantidade": quantidade,
                "valor_previsto": round(valor, 2),
            }

    def listar_pendencias(self, competencia: Optional[int] = None) -> List[Dict[str, Any]]:
        if competencia is None:
            competencia = int(datetime.now().strftime("%Y%m"))
        query = """
            SELECT
                L.ID_LANCAMENTO,
                D.DESCRICAO,
                L.DT_VENCIMENTO,
                L.VL_PREVISTO,
                L.STATUS
            FROM TB_DESPESAS_FIXAS_LANCAMENTOS L WITH(NOLOCK)
            INNER JOIN TB_DESPESAS_FIXAS D WITH(NOLOCK) ON D.ID_DESPESA_FIXA = L.ID_DESPESA_FIXA
            WHERE L.COMPETENCIA = ?
              AND L.STATUS = 'AGUARDANDO'
            ORDER BY L.DT_VENCIMENTO, D.DESCRICAO
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            rows = cursor.execute(query, competencia).fetchall()
            result: List[Dict[str, Any]] = []
            for row in rows:
                result.append(
                    {
                        "id_lancamento": row.ID_LANCAMENTO,
                        "descricao": row.DESCRICAO,
                        "data_vencimento": row.DT_VENCIMENTO.strftime("%Y-%m-%d") if row.DT_VENCIMENTO else None,
                        "valor_previsto": float(row.VL_PREVISTO or 0),
                        "status": row.STATUS,
                    }
                )
            return result

    def processar_competencia(self, competencia: Optional[int], id_usuario: int) -> int:
        if competencia is None:
            competencia = int(datetime.now().strftime("%Y%m"))
        query = """
SET NOCOUNT ON;
DECLARE @competencia INT = ?;
DECLARE @ano INT = @competencia / 100;
DECLARE @mes INT = @competencia % 100;
DECLARE @usuario INT = ?;

INSERT INTO TB_DESPESAS_FIXAS_LANCAMENTOS
    (ID_DESPESA_FIXA, COMPETENCIA, DT_VENCIMENTO, VL_PREVISTO, STATUS, ID_USUARIO_CRIACAO)
SELECT
    D.ID_DESPESA_FIXA,
    @competencia,
    CASE 
        WHEN D.DIA_VENCIMENTO IS NULL OR D.DIA_VENCIMENTO < 1 THEN DATEFROMPARTS(@ano, @mes, 1)
        WHEN D.DIA_VENCIMENTO > DAY(EOMONTH(DATEFROMPARTS(@ano, @mes, 1))) THEN EOMONTH(DATEFROMPARTS(@ano, @mes, 1))
        ELSE DATEFROMPARTS(@ano, @mes, D.DIA_VENCIMENTO)
    END,
    D.VALOR_PADRAO,
    'AGUARDANDO',
    @usuario
FROM TB_DESPESAS_FIXAS D WITH(NOLOCK)
WHERE COALESCE(D.ATIVA, 1) = 1
  AND NOT EXISTS (
      SELECT 1
      FROM TB_DESPESAS_FIXAS_LANCAMENTOS L
      WHERE L.ID_DESPESA_FIXA = D.ID_DESPESA_FIXA
        AND L.COMPETENCIA = @competencia
  );

DECLARE @rows INT = @@ROWCOUNT;
SELECT @rows AS Inseridos;
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (competencia, id_usuario))
            row = cursor.fetchone()
            inseridos = int(row[0] or 0)
            conn.commit()
            return inseridos

    def confirmar_lancamento(self, id_lancamento: int, valor_confirmado: Optional[float], id_usuario: int) -> bool:
        query = """
            UPDATE TB_DESPESAS_FIXAS_LANCAMENTOS
            SET STATUS = 'CONFIRMADO',
                VL_CONFIRMADO = COALESCE(?, VL_PREVISTO),
                DT_CONFIRMACAO = GETDATE(),
                ID_USUARIO_CONFIRMACAO = ?
            WHERE ID_LANCAMENTO = ?
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (valor_confirmado, id_usuario, id_lancamento))
            affected = cursor.rowcount
            conn.commit()
            return affected > 0

    def auto_confirmar_valor_padrao(self, id_usuario: int) -> int:
        query = """
            UPDATE TB_DESPESAS_FIXAS_LANCAMENTOS
            SET STATUS = 'CONFIRMADO_AUTOMATICO',
                VL_CONFIRMADO = VL_PREVISTO,
                DT_CONFIRMACAO = GETDATE(),
                ID_USUARIO_CONFIRMACAO = ?
            WHERE STATUS = 'AGUARDANDO'
              AND DT_VENCIMENTO <= CAST(GETDATE() AS DATE)
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, id_usuario)
            affected = cursor.rowcount
            conn.commit()
            return affected
