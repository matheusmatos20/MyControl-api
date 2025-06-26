from pydantic import BaseModel

class CargoSchema(BaseModel):
    id_cargo: int
    ds_cargo: str