from sqlite3 import Date
from pydantic import BaseModel

class ColaboradorSchema(BaseModel):
    id_funcionario: int
    nm_funcionario: str
    dt_nascimento: Date
    cd_cpf: str
    cd_rg: str
    id_usuario: int

