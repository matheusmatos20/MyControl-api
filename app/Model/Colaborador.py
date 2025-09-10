import pyodbc
import pandas as pd
from datetime import datetime
from Model import Conn_DB
from Schemas import Colaborador as colaborador

class ColaboradorDAL:
    def __init__(self):
        self.conexao = Conn_DB.Conn()
        self.id_servico = None
        self.ds_servico = None
        self.vl_servico = None
        self.fl_recorrente = None
        

    def _connect(self):
        return pyodbc.connect(self.conexao.str_conn)

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
                                          ,case when StatusColaborador is null then 'Inativo' else StatusColaborador end as StatusColaborador
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

    def inserir_colaborador(self,colaborador):
        query = f""" 
                INSERT INTO [dbo].[TB_FUNCIONARIOS]
           ([NM_FUNCIONARIO]
           ,[DT_NASCIMENTO]
           ,[CD_CPF]
           ,[CD_RG]
           ,[ID_USUARIO]) 
     VALUES
           ('{colaborador.nm_funcionario}'
           ,'{colaborador.dt_nascimento}'
           ,'{colaborador.cd_cpf}'
           ,'{colaborador.cd_rg}'
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
   
    def alterar_colaborador(self,colaborador):
        query = f"""
        UPDATE [dbo].[TB_FUNCIONARIOS]
        SET [NM_FUNCIONARIO] = '{colaborador.nm_funcionario}'
            ,[DT_NASCIMENTO] = '{colaborador.dt_nascimento}'
            ,[CD_CPF] = '{colaborador.cd_cpf}'
            ,[CD_RG] = '{colaborador.cd_rg}'
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

    # ...existing code...

    def inserir_colaborador_cargo(self, colaborador, colaborador_cargo):
        print('Model')
        query_funcionario = f""" 
            INSERT INTO [dbo].[TB_FUNCIONARIOS]
                ([NM_FUNCIONARIO], [DT_NASCIMENTO], [CD_CPF], [CD_RG], [ID_USUARIO]) 
            VALUES
                ('{colaborador.nm_funcionario}',
                 '{colaborador.dt_nascimento}',
                 '{colaborador.cd_cpf}',
                 '{colaborador.cd_rg}',
                 {colaborador.id_usuario});
            
             
                    INSERT INTO [dbo].[TB_CARGOS_FUNCIONARIOS]
                        ([ID_FUNCIONARIO], [DT_CARGO], [VL_SALARIO], [ID_USUARIO], [VL_TRANSPORTE], [VL_ALIMENTACAO],
                         [VL_PLANO_SAUDE], [VL_REFEICAO], [VL_INSS], [VL_FGTS], [DT_DESLIGAMENTO], [ID_CARGO])
                    
                    SELECT SCOPE_IDENTITY(),
                         '{colaborador_cargo.dt_cargo}',
                         {colaborador_cargo.vl_salario},
                         {colaborador_cargo.id_usuario},
                         {colaborador_cargo.vl_transporte if colaborador_cargo.vl_transporte is not None else 'NULL'},
                         {colaborador_cargo.vl_alimentacao if colaborador_cargo.vl_alimentacao is not None else 'NULL'},
                         {colaborador_cargo.vl_plano_saude if colaborador_cargo.vl_plano_saude is not None else 'NULL'},
                         {colaborador_cargo.vl_refeicao if colaborador_cargo.vl_refeicao is not None else 'NULL'},
                         {colaborador_cargo.vl_inss if colaborador_cargo.vl_inss is not None else 'NULL'},
                         {colaborador_cargo.vl_fgts if colaborador_cargo.vl_fgts is not None else 'NULL'},
                         CASE WHEN '{colaborador_cargo.dt_desligamento}' = 'None' then NULL ELSE '{colaborador_cargo.dt_desligamento}' END,
                         {colaborador_cargo.id_cargo}"""
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
        
    def atualiza_colaborador_cargo(self, colaborador, colaborador_cargo):
        print('Model')
        query_funcionario = f""" 
            UPDATE [dbo].[TB_FUNCIONARIOS]
                SET [NM_FUNCIONARIO] = '{colaborador.nm_funcionario}',
                 [DT_NASCIMENTO] = '{colaborador.dt_nascimento}',
                 [CD_CPF] = '{colaborador.cd_cpf}',
                 [CD_RG] = '{colaborador.cd_rg}',
                 [ID_USUARIO] = {colaborador.id_usuario}
            WHERE ID_FUNCIONARIO = {colaborador.id_funcionario};
            
            
            UPDATE [dbo].[TB_CARGOS_FUNCIONARIOS]
                    
            SET 
                        [DT_CARGO] =  '{colaborador_cargo.dt_cargo}',
                         [VL_SALARIO] = {colaborador_cargo.vl_salario},
                         [ID_USUARIO] = {colaborador_cargo.id_usuario},
                         [VL_TRANSPORTE] = {colaborador_cargo.vl_transporte if colaborador_cargo.vl_transporte is not None else 'NULL'},
                         [VL_ALIMENTACAO] = {colaborador_cargo.vl_alimentacao if colaborador_cargo.vl_alimentacao is not None else 'NULL'},
                         [VL_PLANO_SAUDE] = {colaborador_cargo.vl_plano_saude if colaborador_cargo.vl_plano_saude is not None else 'NULL'},
                         [VL_REFEICAO] = {colaborador_cargo.vl_refeicao if colaborador_cargo.vl_refeicao is not None else 'NULL'},
                         [VL_INSS] = {colaborador_cargo.vl_inss if colaborador_cargo.vl_inss is not None else 'NULL'},
                         [VL_FGTS] = {colaborador_cargo.vl_fgts if colaborador_cargo.vl_fgts is not None else 'NULL'},
                        [DT_DESLIGAMENTO] =  CASE WHEN '{colaborador_cargo.dt_desligamento}' = 'None' then NULL ELSE '{colaborador_cargo.dt_desligamento}' END
                WHERE ID_CARGO = {colaborador_cargo.id_cargo}
                 AND ID_FUNCIONARIO = {colaborador.id_funcionario}
                 AND DT_DESLIGAMENTO IS NULL"""
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