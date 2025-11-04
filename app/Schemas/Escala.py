from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class EscalaSchema(BaseModel):
    id_escala: Optional[int] = None
    id_funcionario: int
    id_posto: int
    data: date
    turno: Optional[str] = None
    observacao: Optional[str] = None


class GerarEscalaSchema(BaseModel):
    periodo_inicio: date = Field(..., description="Data de início do período")
    periodo_fim: date = Field(..., description="Data de fim do período")
    id_postos: Optional[List[int]] = None
    id_cargos: Optional[List[int]] = None
    limpar_existente: bool = True
    # Reservado para futuras folgas e preferências
    # folgas: Optional[Dict[int, List[date]]] = None


class FolgaSchema(BaseModel):
    id_folga: Optional[int] = None
    id_funcionario: int
    data: date
    observacao: Optional[str] = None
