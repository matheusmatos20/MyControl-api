from pydantic import BaseModel
from typing import Optional


class ProcessarRecorrenciaSchema(BaseModel):
    competencia: Optional[int] = None


class FinalizarServicoRecorrenteSchema(BaseModel):
    id_servico_cliente: int
    data_fim: Optional[str] = None
