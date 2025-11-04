from pydantic import BaseModel, Field, validator
from typing import Optional


class ParcelamentoCreateSchema(BaseModel):
    descricao: str = Field(..., max_length=200)
    id_fornecedor: Optional[int] = None
    id_usuario: int
    valor_total: float = Field(..., gt=0)
    numero_parcelas: int = Field(..., gt=0, le=120)
    juros_percentual: Optional[float] = 0
    data_primeira_parcela: str
    id_forma_pagamento: int

    @validator('descricao')
    def _descricao_obrigatoria(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError('Descrição do parcelamento é obrigatória.')
        return value.strip()
