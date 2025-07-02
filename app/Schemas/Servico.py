from pydantic import BaseModel

class ServicoSchema(BaseModel):
    id_servico: int
    ds_servico: str
    vl_servico: float
    fl_recorrente: int