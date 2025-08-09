from sqlite3 import Date
from pydantic import BaseModel

class ServicoClienteSchema(BaseModel):
    id_servico: int
    id_cliente: int
    vl_servico: float
    vl_desconto: float
    dt_servico: Date
    id_usuario: int 
