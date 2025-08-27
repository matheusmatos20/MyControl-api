from pydantic import BaseModel

class FinanceiroSchema(BaseModel):
     dsLancamento: str
     dtLancamento: str  # Assuming this is a string in 'YYYY-MM-DD' format
     idFornecedor: int
     qtMesesGarantia: int
     qtParcelas: int
     dsParcela: str
     numParcela: int
     dtParcela: str  # Assuming this is a string in 'YYYY-MM-DD' format
     vlParcela: float

