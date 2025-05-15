from pathlib import Path
from typing import Annotated, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from Model import Representantes as Representante,Cliente as Cliente
from Schemas import Representante as RepresentanteSchena,Cliente as ClienteSchema
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

app = FastAPI(
    title="Fast Api Fia",
    version="0.1.0",
    description="Minha api",
)


# Usuário simulado
fake_user = {
    "username": "usuario",
    "hashed_password": "$2b$12$fCkQx68K20XyyUxjzY4RjeQYN.ukU5C/09UkSvVdsqYd2iFbZxIhW",  # Substitua com um hash real
}

# Configurações do JWT
SECRET_KEY = "sua_chave_secreta_segura"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    if username != fake_user["username"]:
        return False
    if not verify_password(password, fake_user["hashed_password"]):
        return False
    return {"username": username}

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Função para extrair e validar o token JWT
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return {"username": username}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Credenciais incorretas")
    
    access_token = create_access_token(
        data={"sub": user["username"]}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ---------------------
# Endpoints protegidos
# ---------------------
@app.get("/Representantes")
async def Consultar_Representantes(current_user: dict = Depends(get_current_user)):
    dal = Representante.RepresentanteDAL()
    df = dal.retorna_representantes()
    return df.to_dict(orient="records")

@app.get("/RepresentantesComboBox")
async def Retorna_representante_combo(user: dict = Depends(get_current_user)):
    dal = Representante.RepresentanteDAL()
    df = dal.retorna_representante_combo()
    return df.to_dict(orient="records")

@app.post("/AlterarRepresentante/")
def Alterar_Representante(cliente: RepresentanteSchena.RepresentanteSchema, user: dict = Depends(get_current_user)):
    try:
        nascimento_formatado = datetime.strptime(cliente.dt_nascimento, "%d/%m/%Y").date()
        dal = Representante.RepresentanteDAL()
        df = dal.alterar_representante(cliente)
        return {
            "mensagem": "Representante Alterado com sucesso!",
            "dados": {
                "id_cliente": cliente.id_cliente,
                "nm_cliente": cliente.nm_cliente,
                "dt_nascimento": nascimento_formatado.isoformat(),
                "cpf": cliente.cpf,
                "rg": cliente.rg,
                "telefone": cliente.telefone
            }
        }
    except ValueError as e:
        return {"erro": f"Formato de data inválido: {str(e)}"}

@app.post("/InserirRepresentante/")
def Inserir_Representate(cliente: RepresentanteSchena.RepresentanteSchema, user: dict = Depends(get_current_user)):
    try:
        nascimento_formatado = datetime.strptime(cliente.dt_nascimento, "%d/%m/%Y").date()
        dal = Representante.RepresentanteDAL()
        df = dal.inserir_representante(cliente)
        return {
            "mensagem": "Representante Inserido com sucesso!",
            "dados": {
                "id_cliente": cliente.id_cliente,
                "nm_cliente": cliente.nm_cliente,
                "dt_nascimento": nascimento_formatado.isoformat(),
                "cpf": cliente.cpf,
                "rg": cliente.rg,
                "telefone": cliente.telefone
            }
        }
    except ValueError as e:
        return {"erro": f"Formato de data inválido: {str(e)}"}



#-----------#
# Clientes  #
#-----------#

@app.get("/Clientes")
async def Consultar_Clientes(current_user: dict = Depends(get_current_user)):
    dal = Cliente.Cliente()
    df = dal.retorna_clientes()
    return df.to_dict(orient="records")

@app.get("/ClientesComboBox")
async def Retorna_representante_combo(user: dict = Depends(get_current_user)):
    dal = Cliente.Cliente()
    df = dal.retorna_clientes_combo_box()
    return df.to_dict(orient="records")

@app.post("/AlterarCliente/")
def Alterar_Cliente(cliente: ClienteSchema.ClienteSchema, user: dict = Depends(get_current_user)):
    try:
        nascimento_formatado = datetime.strptime(cliente.dt_nascimento, "%d/%m/%Y").date()
        dal = Cliente.Cliente()
        df = dal.alterar_cliente(cliente)
        return {
            "mensagem": "Cliente Alterado com sucesso!",
            "dados": {
                "id_cliente": cliente.id_cliente,
                "nm_cliente": cliente.nm_cliente,
                "dt_nascimento": nascimento_formatado.isoformat(),
                "cpf": cliente.cpf,
                "rg": cliente.rg,
                "telefone": cliente.telefone
            }
        }
    except ValueError as e:
        return {"erro": f"Formato de data inválido: {str(e)}"}

@app.post("/InserirCliente/")
def Inserir_Cliente(cliente: ClienteSchema.ClienteSchema, user: dict = Depends(get_current_user)):
    try:
        nascimento_formatado = datetime.strptime(cliente.dt_nascimento, "%d/%m/%Y").date()
        dal = Cliente.Cliente()
        df = dal.inserir_cliente(cliente)
        return {
            "mensagem": "Cliente Inserido com sucesso!",
            "dados": {
                "id_cliente": cliente.id_cliente,
                "nm_cliente": cliente.nm_cliente,
                "dt_nascimento": nascimento_formatado.isoformat(),
                "cpf": cliente.cpf,
                "rg": cliente.rg,
                "telefone": cliente.telefone
            }
        }
    except ValueError as e:
        return {"erro": f"Formato de data inválido: {str(e)}"}
