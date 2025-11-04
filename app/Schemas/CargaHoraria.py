from pydantic import BaseModel
from typing import Optional


class CargaHorariaSchema(BaseModel):
    id_carga_horaria: Optional[int] = None
    ds_carga_horaria: str
    qt_horas_semanais: Optional[int] = None

