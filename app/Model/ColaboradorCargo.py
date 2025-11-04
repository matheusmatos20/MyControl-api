import pyodbc
import pandas as pd
from datetime import datetime
from decimal import Decimal, InvalidOperation
from Model.Conn_DB import Conn as Conn_DB
from Schemas import ColaboradorCargo as cargoSchema


class ColaboradorCargoDAL:
    def __init__(self):
        self.conexao = Conn_DB()
        self.id_cargo_funcionario = None
        self.id_funcionario = None
        self.dt_cargo = None
        self.vl_salario = None
        self.id_usuario = None
        self.vl_transporte = None
        self.vl_alimentacao = None
        self.vl_plano_saude = None
        self.vl_refeicao = None
        self.vl_inss = None
        self.vl_fgts = None
        self.dt_desligamento = None
        self.id_cargo = None

    def _connect(self):
        return pyodbc.connect(self.conexao.str_conn)

    def _parse_date(self, value):
        if not value:
            return None
        value = str(value).strip()
        if not value:
            return None
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(value[:10], fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(value[:10]).strftime("%Y-%m-%d")
        except ValueError:
            return None

    def _date_literal(self, value, *, default_today=False, allow_null=True):
        parsed = self._parse_date(value)
        if parsed:
            return f"CONVERT(DATE, '{parsed}', 120)"
        if default_today:
            return "CAST(GETDATE() AS DATE)"
        if allow_null:
            return "NULL"
        return "CAST(GETDATE() AS DATE)"

    def _decimal_literal(self, value):
        if value is None or value == "":
            return "NULL"
        try:
            dec = Decimal(str(value).replace(',', '.'))
            return str(dec)
        except (InvalidOperation, ValueError, TypeError):
            try:
                return str(float(value))
            except (TypeError, ValueError):
                return "NULL"

    def retorna_cargos_colaborador(self):
        query = """
            SELECT 
                CF.ID_CARGO_FUNCIONARIO AS IdCargoFuncionario,
                CF.ID_FUNCIONARIO AS IdFuncionario,
                CONVERT(DATE, CF.DT_CARGO, 103) AS DataCargo,
                CF.VL_SALARIO AS Salario,
                CF.ID_USUARIO AS IdUsuario,
                CF.VL_TRANSPORTE AS Transporte,
                CF.VL_ALIMENTACAO AS Alimentacao,
                CF.VL_PLANO_SAUDE AS PlanoSaude,
                CF.VL_REFEICAO AS Refeicao,
                CF.VL_INSS AS INSS,
                CF.VL_FGTS AS FGTS,
                CONVERT(DATE, CF.DT_DESLIGAMENTO, 103) AS DataDesligamento,
                C.DS_CARGO AS Cargo
            FROM TB_CARGOS_FUNCIONARIOS CF WITH(NOLOCK)
            LEFT JOIN TB_CARGOS C WITH(NOLOCK)
                ON C.ID_CARGO = CF.ID_CARGO
        """
        try:
            with self._connect() as conn:
                return pd.read_sql(query, conn)
        except Exception as e:
            print("Erro ao buscar cargos do colaborador:", e)
            return pd.DataFrame()

    def retorna_cargo_colaborador(self, id_funcionario: int):
        query = f"""
            SELECT 
                CF.ID_CARGO_FUNCIONARIO AS IdCargoFuncionario,
                CF.ID_FUNCIONARIO AS IdFuncionario,
                CONVERT(DATE, CF.DT_CARGO, 103) AS DataCargo,
                CF.VL_SALARIO AS Salario,
                CF.ID_USUARIO AS IdUsuario,
                CF.VL_TRANSPORTE AS Transporte,
                CF.VL_ALIMENTACAO AS Alimentacao,
                CF.VL_PLANO_SAUDE AS PlanoSaude,
                CF.VL_REFEICAO AS Refeicao,
                CF.VL_INSS AS INSS,
                CF.VL_FGTS AS FGTS,
                CONVERT(DATE, CF.DT_DESLIGAMENTO, 103) AS DataDesligamento,
                C.DS_CARGO AS Cargo
            FROM TB_CARGOS_FUNCIONARIOS CF WITH(NOLOCK)
            LEFT JOIN TB_CARGOS C WITH(NOLOCK)
                ON C.ID_CARGO = CF.ID_CARGO
            WHERE CF.ID_FUNCIONARIO = {id_funcionario}
        """
        try:
            with self._connect() as conn:
                return pd.read_sql(query, conn)
        except Exception as e:
            print("Erro ao buscar cargos do colaborador:", e)
            return pd.DataFrame()

    def inserir_cargo_colaborador(self, cargo: cargoSchema):
        dt_cargo_literal = self._date_literal(getattr(cargo, "dt_cargo", None), default_today=True, allow_null=False)
        dt_desligamento_literal = self._date_literal(getattr(cargo, "dt_desligamento", None), allow_null=True)
        dt_desligamento_anterior = self._date_literal(getattr(cargo, "dt_cargo", None), default_today=True, allow_null=False)

        update_query = f"""
            UPDATE TB_CARGOS_FUNCIONARIOS
            SET DT_DESLIGAMENTO = {dt_desligamento_anterior}
            WHERE ID_FUNCIONARIO = {cargo.id_funcionario}
              AND DT_DESLIGAMENTO IS NULL
        """

        insert_query = f"""
            INSERT INTO TB_CARGOS_FUNCIONARIOS (
                ID_FUNCIONARIO, DT_CARGO, VL_SALARIO, ID_USUARIO,
                VL_TRANSPORTE, VL_ALIMENTACAO, VL_PLANO_SAUDE,
                VL_REFEICAO, VL_INSS, VL_FGTS, DT_DESLIGAMENTO, ID_CARGO
            )
            VALUES (
                {cargo.id_funcionario},
                {dt_cargo_literal},
                {self._decimal_literal(getattr(cargo, 'vl_salario', None))},
                {cargo.id_usuario},
                {self._decimal_literal(getattr(cargo, 'vl_transporte', None))},
                {self._decimal_literal(getattr(cargo, 'vl_alimentacao', None))},
                {self._decimal_literal(getattr(cargo, 'vl_plano_saude', None))},
                {self._decimal_literal(getattr(cargo, 'vl_refeicao', None))},
                {self._decimal_literal(getattr(cargo, 'vl_inss', None))},
                {self._decimal_literal(getattr(cargo, 'vl_fgts', None))},
                {dt_desligamento_literal},
                {cargo.id_cargo}
            )
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(update_query)
                cursor.execute(insert_query)
                conn.commit()
                return True
        except Exception as e:
            print("Erro ao inserir cargo do colaborador:", e)
            return False

    def alterar_cargo_colaborador(self, cargo: cargoSchema):
        dt_cargo_literal = self._date_literal(getattr(cargo, "dt_cargo", None), default_today=True, allow_null=False)
        dt_desligamento_literal = self._date_literal(getattr(cargo, "dt_desligamento", None), allow_null=True)
        query = f"""
            UPDATE TB_CARGOS_FUNCIONARIOS
            SET 
                ID_FUNCIONARIO = {cargo.id_funcionario},
                DT_CARGO = {dt_cargo_literal},
                VL_SALARIO = {self._decimal_literal(getattr(cargo, 'vl_salario', None))},
                ID_USUARIO = {cargo.id_usuario},
                VL_TRANSPORTE = {self._decimal_literal(getattr(cargo, 'vl_transporte', None))},
                VL_ALIMENTACAO = {self._decimal_literal(getattr(cargo, 'vl_alimentacao', None))},
                VL_PLANO_SAUDE = {self._decimal_literal(getattr(cargo, 'vl_plano_saude', None))},
                VL_REFEICAO = {self._decimal_literal(getattr(cargo, 'vl_refeicao', None))},
                VL_INSS = {self._decimal_literal(getattr(cargo, 'vl_inss', None))},
                VL_FGTS = {self._decimal_literal(getattr(cargo, 'vl_fgts', None))},
                DT_DESLIGAMENTO = {dt_desligamento_literal},
                ID_CARGO = {cargo.id_cargo}
            WHERE ID_CARGO_FUNCIONARIO = {cargo.id_cargo_funcionario}
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                return True
        except Exception as e:
            print("Erro ao alterar cargo do colaborador:", e)
            return False
