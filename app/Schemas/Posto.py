from pydantic import BaseModel
from typing import Optional


class PostoSchema(BaseModel):
    id_posto: Optional[int] = None
    nm_posto: str
    id_carga_horaria: int
    qt_colaboradores: int

