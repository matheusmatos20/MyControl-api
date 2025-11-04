from pydantic import BaseModel
from typing import Optional


class DespesaFixaConfirmacaoSchema(BaseModel):
    id_lancamento: int
    valor_confirmado: Optional[float] = None
