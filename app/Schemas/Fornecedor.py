from pydantic import BaseModel

class FornecedorSchema(BaseModel):
    id_fornecedor: int
    nm_razao_social: str
    nm_fantasia: str
    cd_cnpj: str  # formato 'dd/mm/yyyy'
    ds_endereco: str
    nu_telefone: str  
