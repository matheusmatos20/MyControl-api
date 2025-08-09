from pydantic import BaseModel

class RepresentanteSchema(BaseModel):
    id_cliente: int
    nm_cliente: str
    dt_nascimento: str  # formato 'dd/mm/yyyy'
    cpf: str
    rg: str
    telefone: str 
