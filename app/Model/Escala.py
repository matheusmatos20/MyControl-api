import pyodbc
import pandas as pd
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any

from Model import Conn_DB
from Schemas import CargaHoraria as carga_schema
from Schemas import Posto as posto_schema
from Schemas import Escala as escala_schema


class EscalaDAL:
    def __init__(self):
        self.conexao = Conn_DB.Conn()

    def _connect(self):
        return pyodbc.connect(self.conexao.str_conn)

    # -------------
    # Util helpers
    # -------------
    def _escape(self, s: Optional[str]) -> str:
        if s is None:
            return ""
        return str(s).replace("'", "''")

    def _q(self, s: Optional[str]) -> str:
        if s is None:
            return "NULL"
        s = str(s).strip()
        if not s:
            return "NULL"
        return f"'{self._escape(s)}'"

    def _dq(self, d: Optional[date]) -> str:
        if not d:
            return "NULL"
        if isinstance(d, str):
            try:
                d = datetime.fromisoformat(d[:10]).date()
            except Exception:
                return self._q(d)
        return f"'{d.isoformat()}'"

    # ------------------------
    # Carga Horária (CRUD)
    # ------------------------
    def inserir_carga_horaria(self, carga: carga_schema.CargaHorariaSchema) -> bool:
        query = f"""
        INSERT INTO TB_CARGA_HORARIA (DS_CARGA_HORARIA, QT_HORAS_SEMANAIS)
        SELECT {self._q(carga.ds_carga_horaria)}, {carga.qt_horas_semanais if carga.qt_horas_semanais is not None else 'NULL'}
        """
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                conn.commit()
                return True
        except Exception:
            return False

    def listar_carga_horaria(self) -> List[Dict[str, Any]]:
        query = """
        SELECT ID_CARGA_HORARIA AS ID, DS_CARGA_HORARIA AS Descricao, QT_HORAS_SEMANAIS AS HorasSemanais
        FROM TB_CARGA_HORARIA WITH(NOLOCK)
        ORDER BY ID_CARGA_HORARIA
        """
        with self._connect() as conn:
            df = pd.read_sql(query, conn)
            return df.to_dict(orient="records")

    def deletar_carga_horaria(self, id_carga: int) -> bool:
        # Impede exclusão quando houver postos ou escala vinculados
        id_carga = int(id_carga)
        with self._connect() as conn:
            cur = conn.cursor()
            # Verifica referência em postos
            cur.execute(
                f"SELECT COUNT(1) FROM TB_POSTOS WITH(NOLOCK) WHERE ID_CARGA_HORARIA = {id_carga}"
            )
            cnt_postos = cur.fetchone()[0]
            if cnt_postos and int(cnt_postos) > 0:
                return False
            # Verifica referência indireta em escala (via postos)
            cur.execute(
                f"""
                SELECT COUNT(1)
                FROM TB_ESCALA E WITH(NOLOCK)
                JOIN TB_POSTOS P WITH(NOLOCK) ON P.ID_POSTO = E.ID_POSTO
                WHERE P.ID_CARGA_HORARIA = {id_carga}
                """
            )
            cnt_escala = cur.fetchone()[0]
            if cnt_escala and int(cnt_escala) > 0:
                return False
            # Pode excluir
            cur.execute(f"DELETE FROM TB_CARGA_HORARIA WHERE ID_CARGA_HORARIA = {id_carga}")
            conn.commit()
            return True

    # ------------------------
    # Postos (CRUD)
    # ------------------------
    def inserir_posto(self, posto: posto_schema.PostoSchema) -> bool:
        query = f"""
        INSERT INTO TB_POSTOS (NM_POSTO, ID_CARGA_HORARIA, QT_COLABORADORES)
        SELECT {self._q(posto.nm_posto)}, {int(posto.id_carga_horaria)}, {int(posto.qt_colaboradores)}
        """
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                conn.commit()
                return True
        except Exception:
            return False

    def listar_postos(self) -> List[Dict[str, Any]]:
        query = """
        SELECT P.ID_POSTO AS ID,
               P.NM_POSTO AS Posto,
               P.QT_COLABORADORES AS Quantidade,
               CH.ID_CARGA_HORARIA AS IdCarga,
               CH.DS_CARGA_HORARIA AS CargaHoraria
        FROM TB_POSTOS P WITH(NOLOCK)
        LEFT JOIN TB_CARGA_HORARIA CH WITH(NOLOCK) ON CH.ID_CARGA_HORARIA = P.ID_CARGA_HORARIA
        ORDER BY P.ID_POSTO
        """
        with self._connect() as conn:
            df = pd.read_sql(query, conn)
            return df.to_dict(orient="records")

    def atualizar_posto(self, id_posto: int, posto: posto_schema.PostoSchema) -> bool:
        query = f"""
        UPDATE TB_POSTOS
        SET NM_POSTO = {self._q(posto.nm_posto)},
            ID_CARGA_HORARIA = {int(posto.id_carga_horaria)},
            QT_COLABORADORES = {int(posto.qt_colaboradores)}
        WHERE ID_POSTO = {int(id_posto)}
        """
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                conn.commit()
                return True
        except Exception:
            return False

    def deletar_posto(self, id_posto: int) -> bool:
        # Impede exclusão quando houver escala vinculada
        id_posto = int(id_posto)
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT COUNT(1) FROM TB_ESCALA WITH(NOLOCK) WHERE ID_POSTO = {id_posto}")
            cnt = cur.fetchone()[0]
            if cnt and int(cnt) > 0:
                return False
            cur.execute(f"DELETE FROM TB_POSTOS WHERE ID_POSTO = {id_posto}")
            conn.commit()
            return True

    # ------------------------
    # Escala (consultas + geração + CRUD)
    # ------------------------
    def _listar_colaboradores_ativos(self, id_cargos: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        filtro_cargo = ""
        if id_cargos:
            in_cargos = ",".join(str(int(x)) for x in id_cargos)
            # O alias correto da CTE é UC (UltimoCargo)
            filtro_cargo = f" AND UC.ID_CARGO IN ({in_cargos}) "

        query = f"""
        ;WITH UltimoCargo AS (
            SELECT CF.ID_FUNCIONARIO,
                   CF.ID_CARGO,
                   CF.DT_CARGO,
                   CF.DT_DESLIGAMENTO,
                   ROW_NUMBER() OVER (PARTITION BY CF.ID_FUNCIONARIO ORDER BY CF.DT_CARGO DESC, CF.ID_CARGO DESC) AS rn
            FROM TB_CARGOS_FUNCIONARIOS CF WITH(NOLOCK)
        )
        SELECT F.ID_FUNCIONARIO AS Id,
               F.NM_FUNCIONARIO AS Nome,
               UC.ID_CARGO AS IdCargo
        FROM TB_FUNCIONARIOS F WITH(NOLOCK)
        LEFT JOIN UltimoCargo UC ON UC.ID_FUNCIONARIO = F.ID_FUNCIONARIO AND UC.rn = 1
        WHERE (UC.DT_DESLIGAMENTO IS NULL OR UC.DT_DESLIGAMENTO = '1900-01-01' OR UC.DT_DESLIGAMENTO = '0001-01-01')
        {filtro_cargo}
        ORDER BY F.ID_FUNCIONARIO
        """
        with self._connect() as conn:
            df = pd.read_sql(query, conn)
            return df.to_dict(orient="records")

    def consultar_escala_funcionario(self, id_funcionario: int) -> List[Dict[str, Any]]:
        query = f"""
        SELECT E.ID_ESCALA AS Id,
               E.ID_FUNCIONARIO AS IdFuncionario,
               E.ID_POSTO AS IdPosto,
               E.DATA AS Data,
               E.TURNO AS Turno,
               E.OBSERVACAO AS Observacao
        FROM TB_ESCALA E WITH(NOLOCK)
        WHERE E.ID_FUNCIONARIO = {int(id_funcionario)}
        ORDER BY E.DATA, E.ID_POSTO
        """
        with self._connect() as conn:
            df = pd.read_sql(query, conn)
            return df.to_dict(orient="records")

    def consultar_escala_posto_dia(self, id_posto: int, data_ref: date) -> List[Dict[str, Any]]:
        data_sql = self._dq(data_ref)
        query = f"""
        SELECT E.ID_ESCALA AS Id,
               E.ID_FUNCIONARIO AS IdFuncionario,
               F.NM_FUNCIONARIO AS NomeFuncionario,
               E.ID_POSTO AS IdPosto,
               E.DATA AS Data,
               E.TURNO AS Turno,
               E.OBSERVACAO AS Observacao
        FROM TB_ESCALA E WITH(NOLOCK)
        LEFT JOIN TB_FUNCIONARIOS F WITH(NOLOCK) ON F.ID_FUNCIONARIO = E.ID_FUNCIONARIO
        WHERE E.ID_POSTO = {int(id_posto)} AND E.DATA = {data_sql}
        ORDER BY E.ID_ESCALA
        """
        with self._connect() as conn:
            df = pd.read_sql(query, conn)
            return df.to_dict(orient="records")

    # Mantido por compatibilidade (não utilizado); use atualizar_escala_item
    def atualizar_escala(self, id_escala: int, escala: escala_schema.EscalaSchema) -> bool:
        return self.atualizar_escala_item(id_escala, escala)

    def atualizar_escala_item(self, id_escala: int, escala: escala_schema.EscalaSchema) -> bool:
        # Valida regras antes de atualizar
        if not self._validar_item_escala(escala.id_funcionario, escala.id_posto, escala.data, ignorar_id=id_escala):
            return False
        query = f"""
        UPDATE TB_ESCALA
        SET ID_FUNCIONARIO = {int(escala.id_funcionario)},
            ID_POSTO = {int(escala.id_posto)},
            DATA = {self._dq(escala.data)},
            TURNO = {self._q(escala.turno)},
            OBSERVACAO = {self._q(escala.observacao)}
        WHERE ID_ESCALA = {int(id_escala)}
        """
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                conn.commit()
                return True
        except Exception:
            return False

    def excluir_escala(self, id_escala: int) -> bool:
        query = f"DELETE FROM TB_ESCALA WHERE ID_ESCALA = {int(id_escala)}"
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                conn.commit()
                return True
        except Exception:
            return False

    def inserir_escala_item(self, escala: escala_schema.EscalaSchema) -> bool:
        # Valida regras antes de inserir
        if not self._validar_item_escala(escala.id_funcionario, escala.id_posto, escala.data):
            return False
        query = f"""
        INSERT INTO TB_ESCALA (ID_FUNCIONARIO, ID_POSTO, DATA, TURNO, OBSERVACAO)
        SELECT {int(escala.id_funcionario)}, {int(escala.id_posto)}, {self._dq(escala.data)}, {self._q(escala.turno)}, {self._q(escala.observacao)}
        """
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                conn.commit()
                return True
        except Exception:
            return False

    def _cargo_atual_funcionario(self, id_funcionario: int) -> Optional[int]:
        query = f"""
        ;WITH UltimoCargo AS (
            SELECT CF.ID_FUNCIONARIO, CF.ID_CARGO,
                   ROW_NUMBER() OVER (PARTITION BY CF.ID_FUNCIONARIO ORDER BY CF.DT_CARGO DESC, CF.ID_CARGO DESC) rn
            FROM TB_CARGOS_FUNCIONARIOS CF WITH(NOLOCK)
        )
        SELECT ID_CARGO FROM UltimoCargo WHERE ID_FUNCIONARIO = {int(id_funcionario)} AND rn = 1
        """
        with self._connect() as conn:
            df = pd.read_sql(query, conn)
            if df.empty:
                return None
            return int(df.iloc[0, 0])

    def _obter_posto(self, id_posto: int) -> Optional[Dict[str, Any]]:
        query = f"""
        SELECT P.ID_POSTO AS IdPosto, P.NM_POSTO AS Posto, CH.DS_CARGA_HORARIA AS CargaHoraria
        FROM TB_POSTOS P WITH(NOLOCK)
        LEFT JOIN TB_CARGA_HORARIA CH WITH(NOLOCK) ON CH.ID_CARGA_HORARIA = P.ID_CARGA_HORARIA
        WHERE P.ID_POSTO = {int(id_posto)}
        """
        with self._connect() as conn:
            df = pd.read_sql(query, conn)
            if df.empty:
                return None
            return df.to_dict(orient="records")[0]

    def _validar_item_escala(self, id_funcionario: int, id_posto: int, data_ref: date, ignorar_id: Optional[int] = None) -> bool:
        where_ignore = f" AND ID_ESCALA <> {int(ignorar_id)}" if ignorar_id else ""
        # duplicidade no mesmo dia
        query_dup = f"""
        SELECT COUNT(1) FROM TB_ESCALA WITH(NOLOCK)
        WHERE ID_FUNCIONARIO = {int(id_funcionario)} AND DATA = {self._dq(data_ref)} {where_ignore}
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(query_dup)
            if int(cur.fetchone()[0]) > 0:
                return False

        posto = self._obter_posto(id_posto)
        if not posto:
            return False

        # Cargo requerido por posto
        cargo_req = self._infer_cargo_por_posto(posto.get("Posto"))
        if cargo_req is not None:
            cargo_func = self._cargo_atual_funcionario(id_funcionario)
            if cargo_func is None or int(cargo_func) != int(cargo_req):
                return False

        # 12x36: sem dias consecutivos
        carga_desc = (posto.get("CargaHoraria") or "").lower()
        if "12x36" in carga_desc:
            prev_day = data_ref - timedelta(days=1)
            next_day = data_ref + timedelta(days=1)
            query12 = f"""
            SELECT COUNT(1) FROM TB_ESCALA WITH(NOLOCK)
            WHERE ID_FUNCIONARIO = {int(id_funcionario)}
              AND DATA IN ({self._dq(prev_day)}, {self._dq(next_day)})
              {where_ignore}
            """
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(query12)
                if int(cur.fetchone()[0]) > 0:
                    return False
        return True

    def _listar_postos_para_geracao(self, id_postos: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        filtro = ""
        if id_postos:
            ids = ",".join(str(int(x)) for x in id_postos)
            filtro = f" WHERE P.ID_POSTO IN ({ids}) "
        query = f"""
        SELECT P.ID_POSTO AS IdPosto,
               P.NM_POSTO AS Posto,
               P.QT_COLABORADORES AS QtColaboradores,
               CH.ID_CARGA_HORARIA AS IdCarga,
               CH.DS_CARGA_HORARIA AS CargaHoraria,
               CH.QT_HORAS_SEMANAIS AS HorasSemanais
        FROM TB_POSTOS P WITH(NOLOCK)
        LEFT JOIN TB_CARGA_HORARIA CH WITH(NOLOCK) ON CH.ID_CARGA_HORARIA = P.ID_CARGA_HORARIA
        {filtro}
        ORDER BY P.ID_POSTO
        """
        with self._connect() as conn:
            df = pd.read_sql(query, conn)
            return df.to_dict(orient="records")

    def _infer_cargo_por_posto(self, nome_posto: Optional[str]) -> Optional[int]:
        if not nome_posto:
            return None
        base = str(nome_posto).lower()
        base = (
            base.encode('ascii', 'ignore').decode('ascii')
        )  # remove acentos para busca simples
        if 'enferm' in base:
            if 'tecn' in base:
                return 2  # Técnica de Enfermagem
            if 'aux' in base:
                return 1  # Auxiliar de Enfermagem
            return 3      # Enfermeira(o)
        if 'nutricion' in base:
            return 5
        if 'limpez' in base:
            return 6
        if 'cuidad' in base:
            return 4
        return None

    def _limpar_escala_periodo(self, data_ini: date, data_fim: date, id_postos: Optional[List[int]] = None) -> None:
        where_postos = ""
        if id_postos:
            ids = ",".join(str(int(x)) for x in id_postos)
            where_postos = f" AND ID_POSTO IN ({ids}) "
        query = f"""
        DELETE FROM TB_ESCALA
        WHERE DATA BETWEEN {self._dq(data_ini)} AND {self._dq(data_fim)}
        {where_postos}
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(query)
            conn.commit()

    def _inserir_escala_lote(self, itens: List[escala_schema.EscalaSchema]) -> int:
        if not itens:
            return 0
        values_sql: List[str] = []
        for it in itens:
            values_sql.append(
                f"({int(it.id_funcionario)}, {int(it.id_posto)}, {self._dq(it.data)}, {self._q(it.turno)}, {self._q(it.observacao)})"
            )
        query = (
            "INSERT INTO TB_ESCALA (ID_FUNCIONARIO, ID_POSTO, DATA, TURNO, OBSERVACAO) SELECT "
            + " UNION ALL SELECT ".join(v.strip("()") for v in values_sql)
        )
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(query)
            conn.commit()
            return len(itens)

    def gerar_escala(self, payload: escala_schema.GerarEscalaSchema) -> List[Dict[str, Any]]:
        data_ini = payload.periodo_inicio
        data_fim = payload.periodo_fim
        if data_fim < data_ini:
            raise ValueError("Período inválido: fim antes do início")

        postos = self._listar_postos_para_geracao(payload.id_postos)
        colaboradores = self._listar_colaboradores_ativos(payload.id_cargos)

        # Carrega folgas no período para evitar alocação nesses dias
        folgas_map = self._mapear_folgas_periodo(data_ini, data_fim)

        if not postos or not colaboradores:
            return []

        if payload.limpar_existente:
            self._limpar_escala_periodo(data_ini, data_fim, payload.id_postos)

        # Round-robin simples, com regra especial para 12x36 (alternância)
        dias: List[date] = []
        d = data_ini
        while d <= data_fim:
            dias.append(d)
            d += timedelta(days=1)

        resultado: List[escala_schema.EscalaSchema] = []
        # Controle de alocacao por dia (evita duplicidade de colaborador no mesmo dia)
        alocado_dia: Dict[date, set] = {}
        # Controle de dias trabalhados para regra 12x36
        dias_trabalhados: Dict[int, set] = {}

        if not colaboradores:
            return []

        for posto in postos:
            qt_needed = int(posto.get("QtColaboradores") or 1)
            carga_desc = (posto.get("CargaHoraria") or "").lower()
            id_posto = int(posto["IdPosto"]) \
                if posto.get("IdPosto") is not None else int(posto.get("ID") or posto.get("ID_POSTO"))
            cargo_req = self._infer_cargo_por_posto(posto.get("Posto"))

            # Seleção inicial: todos colaboradores (filtrados por cargo acima). 
            # Distribuição justa: rotaciona o índice de início por posto
            base_idx = id_posto % len(colaboradores)

            for idx_dia, dia in enumerate(dias):
                # Identificar 12x36
                is_12x36 = "12x36" in carga_desc

                # Candidatos por cargo do posto (se houver)
                if cargo_req:
                    candidatos = [c for c in colaboradores if int(c.get("IdCargo") or 0) == cargo_req]
                    if not candidatos:
                        continue
                else:
                    candidatos = colaboradores

                if is_12x36:
                    # Alternância: define uma paridade pelo dia e pelo colaborador
                    # Para cada posto/dia, pega uma janela de colaboradores suficientemente grande
                    # e escolhe aqueles cujo (indice + dia_index) % 2 == 0 até atingir qt_needed
                    selecionados: List[Dict[str, Any]] = []
                    for j in range(len(candidatos)):
                        col = candidatos[(base_idx + idx_dia + j) % len(candidatos)]
                        if ((base_idx + idx_dia + j) % 2) == 0:
                            selecionados.append(col)
                        if len(selecionados) >= qt_needed:
                            break
                else:
                    # Round-robin simples para outras cargas
                    selecionados = [
                        candidatos[(base_idx + idx_dia + j) % len(candidatos)]
                        for j in range(qt_needed)
                    ]

                for col in selecionados:
                    col_id = int(col["Id"])
                    # pula se colaborador estiver de folga no dia
                    if col_id in folgas_map and dia in folgas_map[col_id]:
                        continue
                    # evita duplicidade no mesmo dia (qualquer posto)
                    if dia in alocado_dia and col_id in alocado_dia[dia]:
                        continue
                    # Regra 12x36: não alocar no dia seguinte/antecessor
                    if is_12x36:
                        prev_day = dia - timedelta(days=1)
                        next_day = dia + timedelta(days=1)
                        dias_col = dias_trabalhados.get(col_id, set())
                        if prev_day in dias_col or next_day in dias_col:
                            continue
                    resultado.append(
                        escala_schema.EscalaSchema(
                            id_funcionario=col_id,
                            id_posto=id_posto,
                            data=dia,
                            turno=None,
                            observacao=None,
                        )
                    )
                    # Marca controles
                    if dia not in alocado_dia:
                        alocado_dia[dia] = set()
                    alocado_dia[dia].add(col_id)
                    dias_trabalhados.setdefault(col_id, set()).add(dia)

        # Inserção em lote
        self._inserir_escala_lote(resultado)

        # Retorna visão gerada (resumida)
        saida: List[Dict[str, Any]] = [
            {
                "id_funcionario": it.id_funcionario,
                "id_posto": it.id_posto,
                "data": it.data.isoformat(),
                "turno": it.turno,
                "observacao": it.observacao,
            }
            for it in resultado
        ]
        return saida

    # ------------------------
    # Folgas
    # ------------------------
    def inserir_folga(self, folga: escala_schema.FolgaSchema) -> bool:
        query = f"""
        INSERT INTO TB_FOLGAS_FUNCIONARIO (ID_FUNCIONARIO, DATA, OBSERVACAO)
        SELECT {int(folga.id_funcionario)}, {self._dq(folga.data)}, {self._q(folga.observacao)}
        """
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                conn.commit()
                return True
        except Exception:
            return False

    def listar_folgas_funcionario(self, id_funcionario: int) -> List[Dict[str, Any]]:
        query = f"""
        SELECT ID_FOLGA AS Id,
               ID_FUNCIONARIO AS IdFuncionario,
               DATA AS Data,
               OBSERVACAO AS Observacao
        FROM TB_FOLGAS_FUNCIONARIO WITH(NOLOCK)
        WHERE ID_FUNCIONARIO = {int(id_funcionario)}
        ORDER BY DATA DESC
        """
        with self._connect() as conn:
            df = pd.read_sql(query, conn)
            return df.to_dict(orient="records")

    def deletar_folga(self, id_folga: int) -> bool:
        query = f"DELETE FROM TB_FOLGAS_FUNCIONARIO WHERE ID_FOLGA = {int(id_folga)}"
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                conn.commit()
                return True
        except Exception:
            return False

    def _mapear_folgas_periodo(self, data_ini: date, data_fim: date) -> Dict[int, set]:
        query = f"""
        SELECT ID_FUNCIONARIO, DATA
        FROM TB_FOLGAS_FUNCIONARIO WITH(NOLOCK)
        WHERE DATA BETWEEN {self._dq(data_ini)} AND {self._dq(data_fim)}
        """
        mapa: Dict[int, set] = {}
        with self._connect() as conn:
            df = pd.read_sql(query, conn)
        for _, row in df.iterrows():
            fid = int(row["ID_FUNCIONARIO"]) if "ID_FUNCIONARIO" in row else int(row["IdFuncionario"]) if "IdFuncionario" in row else int(row[0])
            d = row["DATA"] if "DATA" in row else row["Data"]
            if isinstance(d, str):
                try:
                    d = datetime.fromisoformat(d[:10]).date()
                except Exception:
                    d = datetime.strptime(str(d)[:10], "%Y-%m-%d").date()
            if fid not in mapa:
                mapa[fid] = set()
            mapa[fid].add(d)
        return mapa
