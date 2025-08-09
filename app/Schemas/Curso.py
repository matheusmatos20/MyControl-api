from pydantic import BaseModel

class CursoSchema(BaseModel):
    id_curso: int
    dt_criacao: str
    nm_curso: str
    ds_curso: str