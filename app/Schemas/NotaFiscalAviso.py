from pydantic import BaseModel, constr, validator
from decimal import Decimal
from datetime import date
from typing import Optional

class NotaFiscalAvisoSchema(BaseModel):
    cnpj_fornecedor: constr(strip_whitespace=True, min_length=14)
    cnpj_empresa: constr(strip_whitespace=True, min_length=14)
    numero_nf: constr(strip_whitespace=True, min_length=1)
    serie_nf: constr(strip_whitespace=True, min_length=1)
    chave_nf: Optional[constr(strip_whitespace=True, min_length=44, max_length=44)] = None
    valor: Decimal
    data_emissao: date
    data_vencimento: date
    observacao: Optional[constr(strip_whitespace=True, min_length=1)] = None

    @validator('valor', pre=True)
    def parse_valor(cls, value):
        if isinstance(value, Decimal):
            return value
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        if isinstance(value, str):
            cleaned = value.replace('.', '').replace(',', '.').strip()
            return Decimal(cleaned)
        raise ValueError('Valor inválido')

    class Config:
        anystr_strip_whitespace = True



