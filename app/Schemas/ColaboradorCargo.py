from pydantic import BaseModel
from typing import Optional

class ColaboradorCargoSchema(BaseModel):
    id_cargo_funcionario: Optional[int] = None
    id_funcionario: int
    dt_cargo: str
    vl_salario: float
    id_usuario: int
    vl_transporte: Optional[float] = None
    vl_alimentacao: Optional[float] = None
    vl_plano_saude: Optional[float] = None
    vl_refeicao: Optional[float] = None
    vl_inss: Optional[float] = None
    vl_fgts: Optional[float] = None
    dt_desligamento: Optional[str] = None
    id_cargo: int