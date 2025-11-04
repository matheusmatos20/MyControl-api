import pyodbc
import pandas as pd
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from Model import Conn_DB
from Schemas import Colaborador as colaborador
from Schemas import ColaboradorCargo as colaborador_cargo_schema


class ColaboradorDAL:
    def __init__(self):
        self.conexao = Conn_DB.Conn()

    def _connect(self):
        return pyodbc.connect(self.conexao.str_conn)

    def _escape_string(self, value: Optional[str]) -> str:
        if value is None:
            return ""
        return str(value).replace("'", "''")

    def _string_literal(self, value: Optional[str]) -> str:
        if value is None:
            return "NULL"
        value = str(value).strip()
        if value.lower() in {"null", "none", ""}:
            return "NULL"
        return f"'{self._escape_string(value)}'"

    def _parse_date(self, value: Optional[str]) -> Optional[str]:
        if not value or str(value).lower() in {"null", "none"}:
            return None
        value = str(value).strip()
        candidates = ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d")
        for fmt in candidates:
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

    def _format_date_literal(self, value: Optional[str]) -> str:
        parsed = self._parse_date(value)
        if not parsed:
            return "NULL"
        return f"'{parsed}'"

    def _format_decimal_literal(self, value: Optional[float]) -> str:
        if value is None:
            return "NULL"
        dec = Decimal(str(value))
        dec = dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return str(dec)

    def _sum_optional(self, *values: Optional[float]) -> Decimal:
        total = Decimal("0.00")
        for val in values:
            if val is None:
                continue
            total += Decimal(str(val))
        return total

    def _aliquota_inss(self, salario: Decimal) -> Decimal:
        if salario <= Decimal("1412.00"):
            return Decimal("0.075")
        if salario <= Decimal("2666.68"):
            return Decimal("0.09")
        if salario <= Decimal("4000.03"):
            return Decimal("0.12")
        if salario <= Decimal("7786.02"):
            return Decimal("0.14")
        return Decimal("0.14")

    def _calcular_encargos(self, colaborador_cargo: colaborador_cargo_schema.ColaboradorCargoSchema):
        salario = Decimal(str(colaborador_cargo.vl_salario or 0))
        beneficios = self._sum_optional(
            colaborador_cargo.vl_transporte,
            colaborador_cargo.vl_alimentacao,
            colaborador_cargo.vl_plano_saude,
            colaborador_cargo.vl_refeicao,
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if salario <= 0:
            return {
                "inss": Decimal("0.00"),
                "fgts": Decimal("0.00"),
                "decimo_terceiro": Decimal("0.00"),
                "ferias": Decimal("0.00"),
                "custo_total": beneficios,
            }

        aliquota_inss = self._aliquota_inss(salario)
        valor_inss = (salario * aliquota_inss).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        valor_fgts = (salario * Decimal("0.08")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        parcela_decimo = (salario / Decimal("12")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        parcela_ferias = ((salario / Decimal("13")) * Decimal("1.3")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        custo_total = (salario + beneficios + valor_inss + valor_fgts + parcela_decimo + parcela_ferias).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        return {
            "inss": valor_inss,
            "fgts": valor_fgts,
            "decimo_terceiro": parcela_decimo,
            "ferias": parcela_ferias,
            "custo_total": custo_total,
        }



    def _preparar_valores_cargo(self, colaborador_cargo: colaborador_cargo_schema.ColaboradorCargoSchema):
        encargos = self._calcular_encargos(colaborador_cargo)

        colaborador_cargo.vl_inss = float(encargos["inss"])
        colaborador_cargo.vl_fgts = float(encargos["fgts"])
        colaborador_cargo.vl_prov_decimo_terceiro = float(encargos["decimo_terceiro"])
        colaborador_cargo.vl_prov_ferias = float(encargos["ferias"])
        colaborador_cargo.vl_custo_total = float(encargos["custo_total"])

        return {
            "dt_cargo": self._format_date_literal(colaborador_cargo.dt_cargo),
            "vl_salario": self._format_decimal_literal(colaborador_cargo.vl_salario),
            "id_usuario": colaborador_cargo.id_usuario,
            "vl_transporte": self._format_decimal_literal(colaborador_cargo.vl_transporte),
            "vl_alimentacao": self._format_decimal_literal(colaborador_cargo.vl_alimentacao),
            "vl_plano_saude": self._format_decimal_literal(colaborador_cargo.vl_plano_saude),
            "vl_refeicao": self._format_decimal_literal(colaborador_cargo.vl_refeicao),
            "vl_inss": self._format_decimal_literal(encargos["inss"]),
            "vl_fgts": self._format_decimal_literal(encargos["fgts"]),
            "vl_prov_decimo_terceiro": self._format_decimal_literal(encargos["decimo_terceiro"]),
            "vl_prov_ferias": self._format_decimal_literal(encargos["ferias"]),
            "vl_custo_total": self._format_decimal_literal(encargos["custo_total"]),
            "dt_desligamento": self._format_date_literal(colaborador_cargo.dt_desligamento),
            "id_cargo": colaborador_cargo.id_cargo,
        }

    def retorna_colaborador(self):
        query = """
                 WITH CTE_ULTIMO_CARGO AS (
                    SELECT MAX(DT_CARGO) MAX_DT_CARGO
                    ,ID_FUNCIONARIO
                    FROM TB_CARGOS_FUNCIONARIOS CF WITH(NOLOCK)
                    GROUP BY ID_FUNCIONARIO
                    
                    )
                    ,
                     CTE AS (
                    SELECT 
                    CONCAT(C.ID_CARGO,' - ',C.DS_CARGO) AS Cargo
                    ,CASE WHEN CF.DT_DESLIGAMENTO IS NULL	
					THEN 'Ativo'
					ELSE 'Inativo'
					END                 as StatusColaborador
                    ,CF.ID_FUNCIONARIO
                    ,CF.DT_CARGO		AS DtAdmissao
                    ,CF.VL_FGTS			AS Fgts
                    ,CF.VL_INSS			AS Inss
                    ,CF.VL_PLANO_SAUDE	AS PlanoSaude
                    ,CF.VL_REFEICAO		AS Refeicao
                    ,CF.VL_ALIMENTACAO	AS Alimentacao
                    ,CF.VL_SALARIO		AS Salario
                     ,CF.VL_TRANSPORTE   AS ValeTransporte

                    FROM TB_CARGOS_FUNCIONARIOS CF WITH(NOLOCK)
                    JOIN CTE_ULTIMO_CARGO		CFU WITH(NOLOCK) ON CFU.MAX_DT_CARGO = CF.DT_CARGO AND CFU.ID_FUNCIONARIO = CF.ID_FUNCIONARIO
                    JOIN TB_CARGOS				C WITH(NOLOCK) ON C.ID_CARGO = CF.ID_CARGO
                    )
                    
                    SELECT				   F.ID_FUNCIONARIO as Id
                                          ,F.NM_FUNCIONARIO AS NomeColaborador
                                          ,F.DT_NASCIMENTO    AS DtNascimento
                                          ,F.CD_CPF           AS Cpf
                                          ,F.CD_RG            AS Rg
                                          ,case when Cargo is null then 'Sem Cargo' else Cargo end as Cargo
                    					  ,ISNULL(C.DtAdmissao,'1900-01-01') AS DtAdmissao
										  ,ISNULL(C.Fgts			,0) AS Fgts
										  ,ISNULL(C.Inss			,0) AS Inss
										  ,ISNULL(C.PlanoSaude	,0) AS PlanoSaude
										  ,ISNULL(C.Refeicao		,0) AS Refeicao
                                          ,ISNULL(C.Alimentacao		,0) AS Alimentacao
										  ,ISNULL(C.Salario		,0) AS Salario
										  ,ISNULL(C.ValeTransporte,0) AS ValeTransporte
                                          ,case when StatusColaborador is null then 'Inativo' else StatusColaborador end as StatusColaborador\n
                    FROM dbo.TB_FUNCIONARIOS F WITH(NOLOCK) 
                    LEFT JOIN CTE C ON C.ID_FUNCIONARIO = F.ID_FUNCIONARIO
        """
        with self._connect() as conn:
            return pd.read_sql(query, conn)

    def retorna_colaborador_combo(self):
        query = """
        SELECT CONCAT(ID_FUNCIONARIO, ' - ', NM_FUNCIONARIO) AS Colaborador
        FROM TB_FUNCIONARIOS WITH(NOLOCK)
        ORDER BY ID_FUNCIONARIO
        """
        with self._connect() as conn:
            return pd.read_sql(query, conn)

    def inserir_colaborador(self, colaborador: colaborador.ColaboradorSchema):
        query = f"""
                INSERT INTO [dbo].[TB_FUNCIONARIOS]
           ([NM_FUNCIONARIO]
           ,[DT_NASCIMENTO]
           ,[CD_CPF]
           ,[CD_RG]
           ,[ID_USUARIO]) 
     VALUES
           ({self._string_literal(colaborador.nm_funcionario)}
           ,{self._format_date_literal(colaborador.dt_nascimento)}
           ,{self._string_literal(colaborador.cd_cpf)}
           ,{self._string_literal(colaborador.cd_rg)}
           ,{colaborador.id_usuario}
        )"""
        print(query)
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                return True
        except Exception:
            return False

    def alterar_colaborador(self, colaborador: colaborador.ColaboradorSchema):
        query = f"""
        UPDATE [dbo].[TB_FUNCIONARIOS]
        SET [NM_FUNCIONARIO] = {self._string_literal(colaborador.nm_funcionario)}
            ,[DT_NASCIMENTO] = {self._format_date_literal(colaborador.dt_nascimento)}
            ,[CD_CPF] = {self._string_literal(colaborador.cd_cpf)}
            ,[CD_RG] = {self._string_literal(colaborador.cd_rg)}
            ,[ID_USUARIO] = {colaborador.id_usuario}
        WHERE ID_FUNCIONARIO = {colaborador.id_funcionario}

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

    def inserir_colaborador_cargo(self, colaborador: colaborador.ColaboradorSchema, colaborador_cargo: colaborador_cargo_schema.ColaboradorCargoSchema):
        print('Model inserir_colaborador_cargo')
        valores = self._preparar_valores_cargo(colaborador_cargo)

        query_funcionario = f"""
            DECLARE @ID_FUNCIONARIO INT;

            INSERT INTO [dbo].[TB_FUNCIONARIOS]
                ([NM_FUNCIONARIO], [DT_NASCIMENTO], [CD_CPF], [CD_RG], [ID_USUARIO]) 
            VALUES
                ({self._string_literal(colaborador.nm_funcionario)},
                 {self._format_date_literal(colaborador.dt_nascimento)},
                 {self._string_literal(colaborador.cd_cpf)},
                 {self._string_literal(colaborador.cd_rg)},
                 {colaborador.id_usuario});

            SET @ID_FUNCIONARIO = SCOPE_IDENTITY();

            INSERT INTO [dbo].[TB_CARGOS_FUNCIONARIOS]
                ([ID_FUNCIONARIO], [DT_CARGO], [VL_SALARIO], [ID_USUARIO], [VL_TRANSPORTE], [VL_ALIMENTACAO],
                 [VL_PLANO_SAUDE], [VL_REFEICAO], [VL_INSS], [VL_FGTS], [VL_PROV_DECIMO_TERCEIRO], [VL_PROV_FERIAS],
                 [VL_CUSTO_TOTAL], [DT_DESLIGAMENTO], [ID_CARGO])
            VALUES
                (@ID_FUNCIONARIO,
                 {valores['dt_cargo']},
                 {valores['vl_salario']},
                 {valores['id_usuario']},
                 {valores['vl_transporte']},
                 {valores['vl_alimentacao']},
                 {valores['vl_plano_saude']},
                 {valores['vl_refeicao']},
                 {valores['vl_inss']},
                 {valores['vl_fgts']},
                 {valores['vl_prov_decimo_terceiro']},
                 {valores['vl_prov_ferias']},
                 {valores['vl_custo_total']},
                 {valores['dt_desligamento']},
                 {valores['id_cargo']});
        """
        try:
            print(query_funcionario)
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query_funcionario)
                conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao inserir colaborador e cargo: {e}")
            return False

    def atualiza_colaborador_cargo(self, colaborador: colaborador.ColaboradorSchema, colaborador_cargo: colaborador_cargo_schema.ColaboradorCargoSchema):
        print('Model atualiza_colaborador_cargo')
        valores = self._preparar_valores_cargo(colaborador_cargo)

        if colaborador_cargo.id_cargo_funcionario:
            where_clause = f"ID_CARGO_FUNCIONARIO = {colaborador_cargo.id_cargo_funcionario}"
        else:
            where_clause = f"ID_FUNCIONARIO = {colaborador.id_funcionario} AND ID_CARGO = {colaborador_cargo.id_cargo} AND DT_DESLIGAMENTO IS NULL"

        query_funcionario = f"""
            UPDATE [dbo].[TB_FUNCIONARIOS]
                SET [NM_FUNCIONARIO] = {self._string_literal(colaborador.nm_funcionario)},
                 [DT_NASCIMENTO] = {self._format_date_literal(colaborador.dt_nascimento)},
                 [CD_CPF] = {self._string_literal(colaborador.cd_cpf)},
                 [CD_RG] = {self._string_literal(colaborador.cd_rg)},
                 [ID_USUARIO] = {colaborador.id_usuario}
            WHERE ID_FUNCIONARIO = {colaborador.id_funcionario};

            UPDATE [dbo].[TB_CARGOS_FUNCIONARIOS]
            SET 
                [DT_CARGO] = {valores['dt_cargo']},
                [VL_SALARIO] = {valores['vl_salario']},
                [ID_USUARIO] = {valores['id_usuario']},
                [VL_TRANSPORTE] = {valores['vl_transporte']},
                [VL_ALIMENTACAO] = {valores['vl_alimentacao']},
                [VL_PLANO_SAUDE] = {valores['vl_plano_saude']},
                [VL_REFEICAO] = {valores['vl_refeicao']},
                [VL_INSS] = {valores['vl_inss']},
                [VL_FGTS] = {valores['vl_fgts']},
                [VL_PROV_DECIMO_TERCEIRO] = {valores['vl_prov_decimo_terceiro']},
                [VL_PROV_FERIAS] = {valores['vl_prov_ferias']},
                [VL_CUSTO_TOTAL] = {valores['vl_custo_total']},
                [DT_DESLIGAMENTO] = {valores['dt_desligamento']},
                [ID_CARGO] = {valores['id_cargo']}
            WHERE {where_clause};
        """
        try:
            print(query_funcionario)
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query_funcionario)
                conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar colaborador e cargo: {e}")
            return False
