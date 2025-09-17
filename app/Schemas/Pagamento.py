from pydantic import BaseModel, constr
from typing import Optional
from datetime import date

class PagamentoSchema(BaseModel):
    ds_pagamento: str
    dt_pagamento: Optional[str]  # formato 'dd/mm/yyyy'
    dt_vencimento: str           # formato 'dd/mm/yyyy'
    id_fornecedor: int
    vl_pagamento: str            # Ex: '1234,56' (como string por conta da vírgula)
    id_forma_pagamento: int
    id_usuario: int              # Adicionado pois é usado no INSERT

