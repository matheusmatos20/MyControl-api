from pydantic import BaseModel

class ClienteSchema(BaseModel):
    id_cliente: int
    id_representante: int
    nm_cliente: str
    dt_nascimento: str  # formato 'dd/mm/yyyy'
    cpf: str
    rg: str
    telefone: str  
