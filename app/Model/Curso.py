import pyodbc
import pandas as pd
from datetime import datetime
from Model import Conn_DB
from Schemas import Curso as CursoSchema

class CursoDAL:
    def __init__(self):
        self.conexao = Conn_DB.Conn()

    def _connect(self):
        return pyodbc.connect(self.conexao.str_conn)
    
    def get_cursos(self):
        query = "SELECT * FROM TB_CURSO"
        
        with self._connect() as conn:
            df = pd.read_sql(query, conn)
        return df
    

    def InserirCurso(self,CursoSchema):
        query = f""" 
        INSERT INTO TB_CURSO (dt_criacao, nm_curso, ds_curso) 
        SELECT CONVERT(DATE,'{CursoSchema.dt_criacao}'), '{CursoSchema.nm_curso}', '{CursoSchema.ds_curso}'
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
    # def get_cursos(self) -> pd.DataFrame:
    #     query = "SELECT * FROM curso"
    #     with pyodbc.connect(self.conn.str_conn) as conn:
    #         df = pd.read_sql(query, conn)
    #     return df

    # def get_curso_by_id(self, id_curso: int) -> pd.DataFrame:
    #     query = "SELECT * FROM curso WHERE id_curso = ?"
    #     with pyodbc.connect(self.conn.str_conn) as conn:
    #         df = pd.read_sql(query, conn, params=(id_curso,))
    #     return df

    # def create_curso(self, curso: CursoSchema) -> None:
    #     query = """
    #     INSERT INTO curso (dt_criacao, nm_curso, ds_curso)
    #     VALUES (?, ?, ?)
    #     """
    #     with pyodbc.connect(self.conn.str_conn) as conn:
    #         cursor = conn.cursor()
    #         cursor.execute(query, (curso.dt_criacao, curso.nm_curso, curso.ds_curso))
    #         conn.commit()