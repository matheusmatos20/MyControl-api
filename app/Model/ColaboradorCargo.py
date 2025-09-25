import pyodbc
import pandas as pd
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

    def retorna_cargo_colaborador(self,id_funcionario: int):
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
        query = f"""
            INSERT INTO TB_CARGOS_FUNCIONARIOS (
                ID_FUNCIONARIO, DT_CARGO, VL_SALARIO, ID_USUARIO,
                VL_TRANSPORTE, VL_ALIMENTACAO, VL_PLANO_SAUDE,
                VL_REFEICAO, VL_INSS, VL_FGTS, DT_DESLIGAMENTO, ID_CARGO
            )
            VALUES (
                {cargo.id_funcionario},
                GETDATE(),
                {cargo.vl_salario},
                {cargo.id_usuario},
                {cargo.vl_transporte},
                {cargo.vl_alimentacao},
                {cargo.vl_plano_saude},
                {cargo.vl_refeicao},
                {cargo.vl_inss},
                {cargo.vl_fgts},
                {f"CONVERT(DATE, '{cargo.dt_desligamento}', 103)" if cargo.dt_desligamento else "NULL"},
                {cargo.id_cargo}
            )
        """
        print(query)
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                return True
        except Exception as e:
            print("Erro ao inserir cargo do colaborador:", e)
            return False

    def alterar_cargo_colaborador(self, cargo: cargoSchema):
        query = f"""
            UPDATE TB_CARGOS_FUNCIONARIOS
            SET 
                ID_FUNCIONARIO = {cargo.id_funcionario},
                DT_CARGO = CONVERT(DATE, '{cargo.dt_cargo}', 103),
                VL_SALARIO = {cargo.vl_salario},
                ID_USUARIO = {cargo.id_usuario},
                VL_TRANSPORTE = {cargo.vl_transporte},
                VL_ALIMENTACAO = {cargo.vl_alimentacao},
                VL_PLANO_SAUDE = {cargo.vl_plano_saude},
                VL_REFEICAO = {cargo.vl_refeicao},
                VL_INSS = {cargo.vl_inss},
                VL_FGTS = {cargo.vl_fgts},
                DT_DESLIGAMENTO = {f"CONVERT(DATE, '{cargo.dt_desligamento}', 103)" if cargo.dt_desligamento else "NULL"},
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
