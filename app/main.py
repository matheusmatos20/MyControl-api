from pathlib import Path
from typing import Annotated, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from Model import Representantes as Representante,Cliente as Cliente,Cargo as Cargo,Servico as Servico,Colaborador as Colaborador,Financeiro as Financeiro, Fornecedor as Fornecedor
from Schemas import Representante as RepresentanteSchena,Cliente as ClienteSchema, Cargo as CargoSchema, Servico as ServicoSchema, Colaborador as ColaboradorSchema, ServicoCliente as ServicoClienteSchema, Fornecedor as FornecedorSchema
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # permite POST, GET, OPTIONS, etc
    allow_headers=["*"],
)



# app = FastAPI(
#     title="Fast Api Fia",
#     version="0.1.0",
#     description="Minha api",
# )


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
@app.get("/RetornaDebito",tags=["Financeiro"])
async def Consultar_Debitos(current_user: dict = Depends(get_current_user)):
    dal = Financeiro.FinanceiroDAL()
    df = dal.retorna_pagamentos()
    return df.to_dict(orient="records")

@app.get("/RetornaCredito",tags=["Financeiro"])
async def Consultar_Creditos(current_user: dict = Depends(get_current_user)):
    dal = Financeiro.FinanceiroDAL()
    df = dal.retorna_creditos()
    return df.to_dict(orient="records")

@app.get("/Representantes",tags=["Representantes"])
async def Consultar_Representantes(current_user: dict = Depends(get_current_user)):
    dal = Representante.RepresentanteDAL()
    df = dal.retorna_representantes()
    return df.to_dict(orient="records")

@app.get("/RepresentantesComboBox",tags=["Representantes"])
async def Retorna_representante_combo(user: dict = Depends(get_current_user)):
    dal = Representante.RepresentanteDAL()
    df = dal.retorna_representante_combo()
    return df.to_dict(orient="records")

@app.post("/AlterarRepresentante/",tags=["Representantes"])
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

@app.post("/InserirRepresentante/",tags=["Representantes"])
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

@app.get("/Clientes",tags=["Clientes"])
async def Consultar_Clientes(current_user: dict = Depends(get_current_user)):
    dal = Cliente.Cliente()
    df = dal.retorna_clientes()
    return df.to_dict(orient="records")

@app.get("/ClientesComboBox",tags=["Clientes"])
async def Retorna_representante_combo(user: dict = Depends(get_current_user)):
    dal = Cliente.Cliente()
    df = dal.retorna_clientes_combo_box()
    return df.to_dict(orient="records")

@app.post("/AlterarCliente/",tags=["Clientes"])
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

@app.post("/InserirCliente/",tags=["Clientes"])
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


@app.get("/Cargos",tags=["Cargos"])
async def Consultar_Cargo(current_user: dict = Depends(get_current_user)):
    dal = Cargo.CargoDAL()
    df = dal.retorna_cargos()
    return df.to_dict(orient="records")

@app.get("/CargosComboBox",tags=["Cargos"])
async def Retorna_cargo_combo(user: dict = Depends(get_current_user)):
    dal = Cargo.CargoDAL()
    df = dal.retorna_cargo_combo()
    return df.to_dict(orient="records")

@app.post("/AlterarCargo/",tags=["Cargos"])
def Alterar_Cargo(cargo: CargoSchema.CargoSchema, user: dict = Depends(get_current_user)):
    try:
        dal = Cargo.CargoDAL()
        df = dal.alterar_cargo(cargo)
        return {
            "mensagem": "Cargo Alterado com sucesso!",
            "dados": {
                "id_cargo": cargo.id_cargo,
                "ds_cargo": cargo.ds_cargo,
            }
        }
    except ValueError as e:
        return {"erro": f"Formato de data inválido: {str(e)}"}

@app.post("/InserirCargo/",tags=["Cargos"])
def Inserir_Cargo(cargo: CargoSchema.CargoSchema, user: dict = Depends(get_current_user)):
    try:
        dal = Cargo.Cargo()
        df = dal.InseriCargo(cargo)
        return {
            "mensagem": "Cargo Inserido com sucesso!",
            "dados": {
                "id_cargo": cargo.id_cargp,
                "ds_cliente": cargo.ds_cargo
            }
        }
    except ValueError as e:
        return {"erro": f"Falha na hora de inserir cargo: {str(e)}"}





@app.get("/Servicos",tags=["Serviços"])
async def Consultar_Servicos(current_user: dict = Depends(get_current_user)):
    dal = Servico.ServicoDAL()
    df = dal.retorna_servicos()
    return df.to_dict(orient="records")

@app.get("/ServicosComboBox",tags=["Serviços"])
async def Retorna_servico_combo(user: dict = Depends(get_current_user)):
    dal = Servico.ServicoDAL()
    df = dal.retorna_servico_combo()
    return df.to_dict(orient="records")

@app.post("/AlterarServico/",tags=["Serviços"])
def Alterar_Servico(servico: ServicoSchema.ServicoSchema, user: dict = Depends(get_current_user)):
    try:
        dal = Servico.ServicoDAL()
        df = dal.alterar_servico(servico)
        return {
            "mensagem": "Serviço Alterado com sucesso!",
            "dados": {
                "id_servico": servico.id_servico,
                "ds_servico": servico.ds_servico
            }
        }
    except ValueError as e:
        return {"erro": f"Formato de data inválido: {str(e)}"}

@app.post("/InserirServico/",tags=["Serviços"])
def Inserir_Servico(servico: ServicoSchema.ServicoSchema, user: dict = Depends(get_current_user)):
    try:
        dal = Servico.ServicoDAL()
        df = dal.inserir_servico(servico)
        return {
            "mensagem": "Serviço Inserido com sucesso!",
            "dados": {
                "id_servico": servico.id_servico,
                "ds_servico": servico.ds_servico,
            }
        }
    except ValueError as e:
        return {"erro": f"Falha na hora de inserir Serviço: {str(e)}"}

@app.post("/InserirServicoCliente/",tags=["Serviços"])
def Inserir_Servico_Cliente(servicoCliente: ServicoClienteSchema.ServicoClienteSchema, user: dict = Depends(get_current_user)):
    try:
        dal = Servico.ServicoDAL()
        df = dal.inserir_servico_cliente(servicoCliente)
        return {
            "mensagem": "Colaborador Inserido com sucesso!",
            "dados": {}
        }
    except ValueError as e:
        return {"erro": f"Falha na hora de inserir o Colaborador: {str(e)}"}

@app.get("/ServicosCliente",tags=["Serviços"])
async def Retorna_Servico_cliente(user: dict = Depends(get_current_user)):
    dal = Servico.ServicoDAL()
    df = dal.retorna_servicos_cliente_grid()
    return df.to_dict(orient="records")



@app.get("/Colaboradores",tags=["Colaboradores"])
async def Consultar_Colaborador(current_user: dict = Depends(get_current_user)):
    dal = Colaborador.ColaboradorDAL()
    df = dal.retorna_colaborador()
    return df.to_dict(orient="records")

@app.get("/ColaboradoresComboBox",tags=["Colaboradores"])
async def Retorna_servico_combo(user: dict = Depends(get_current_user)):
    dal = Colaborador.ColaboradorDAL()
    df = dal.retorna_colaborador_combo()
    return df.to_dict(orient="records")

@app.post("/AlterarColaborador/",tags=["Colaboradores"])
def Alterar_Colaborador(colaborador: ColaboradorSchema.ColaboradorSchema, user: dict = Depends(get_current_user)):
    try:
        dal = Colaborador.ColaboradorDAL()
        df = dal.alterar_colaborador(colaborador)
        return {
            "mensagem": "Colaborador Alterado com sucesso!",
            "dados": {
                "id_funcionario": colaborador.id_funcionario,
                "nm_funcionario": colaborador.nm_funcionario
            }
        }
    except ValueError as e:
        return {"erro": f"Formato de data inválido: {str(e)}"}

@app.post("/InserirColaborador/",tags=["Colaboradores"])
def Inserir_Colaborador(colaborador: ColaboradorSchema.ColaboradorSchema, user: dict = Depends(get_current_user)):
    try:
        dal = Colaborador.ColaboradorDAL()
        df = dal.inserir_colaborador(colaborador)
        return {
            "mensagem": "Colaborador Inserido com sucesso!",
            "dados": {
                "id_funcionario": colaborador.id_funcionario,
                "nm_funcionario": colaborador.nm_funcionario,
            }
        }
    except ValueError as e:
        return {"erro": f"Falha na hora de inserir o Colaborador: {str(e)}"}

@app.post("/InserirFornecedor/",tags=["Fornecedores"])
def Inserir_Fornecedor(fornecedor: FornecedorSchema.FornecedorSchema, user: dict = Depends(get_current_user)):
    try:
        dal = Fornecedor.FornecedorDAL()
        df = dal.inserir_fornecedor(fornecedor)
        return {
            "mensagem": "Fornecedor Inserido com sucesso!",
            "dados": {
                "nm_fantasia": fornecedor.nm_fantasia,
            }
        }
    except ValueError as e:
        return {"erro": f"Falha na hora de inserir o Colaborador: {str(e)}"}



@app.get("/RetornaFornecedores",tags=["Fornecedores"])
async def Retorna_fornecedor(user: dict = Depends(get_current_user)):
    dal = Fornecedor.FornecedorDAL()
    df = dal.retorna_fornecedores()
    return df.to_dict(orient="records")


# ...existing code...

from Model import ColaboradorCargo as ColaboradorCargoModel
from Schemas import ColaboradorCargo as ColaboradorCargoSchema

@app.get("/ColaboradoresCargos",tags=["ColaboradoresCargos"])
async def Consultar_Colaborador_Cargos(current_user: dict = Depends(get_current_user)):
    dal = ColaboradorCargoModel.ColaboradorCargoDAL()
    df = dal.retorna_cargos_colaborador()
    return df.to_dict(orient="records")

@app.post("/InserirColaboradorCargo/",tags=["ColaboradoresCargos"])
def Inserir_Colaborador_Cargo(cargo: ColaboradorCargoSchema.ColaboradorCargoSchema, user: dict = Depends(get_current_user)):
    try:
        dal = ColaboradorCargoModel.ColaboradorCargoDAL()
        dal.inserir_cargo_colaborador(cargo)
        return {
            "mensagem": "Cargo de colaborador inserido com sucesso!",
            "dados": cargo.dict()
        }
    except Exception as e:
        return {"erro": f"Falha ao inserir cargo do colaborador: {str(e)}"}

@app.post("/AlterarColaboradorCargo/",tags=["ColaboradoresCargos"])
def Alterar_Colaborador_Cargo(cargo: ColaboradorCargoSchema.ColaboradorCargoSchema, user: dict = Depends(get_current_user)):
    try:
        dal = ColaboradorCargoModel.ColaboradorCargoDAL()
        dal.alterar_cargo_colaborador(cargo)
        return {
            "mensagem": "Cargo de colaborador alterado com sucesso!",
            "dados": cargo.dict()
        }
    except Exception as e:
        return {"erro": f"Falha ao alterar cargo do colaborador: {str(e)}"}
    
# ...existing code...

from Model import Colaborador as ColaboradorModel
from Schemas import Colaborador as ColaboradorSchema, ColaboradorCargo as ColaboradorCargoSchema

@app.post("/InserirColaboradorComCargo/", tags=["Colaboradores"])
def Inserir_Colaborador_Com_Cargo(
    colaborador: ColaboradorSchema.ColaboradorSchema,
    colaborador_cargo: ColaboradorCargoSchema.ColaboradorCargoSchema,
    user: dict = Depends(get_current_user)
):
    print('main')
    dal = ColaboradorModel.ColaboradorDAL()
    resultado = dal.inserir_colaborador_cargo(colaborador, colaborador_cargo)
    if resultado:
        return {"mensagem": "Colaborador e cargo inseridos com sucesso!"}
    else:
        raise HTTPException(status_code=400, detail="Erro ao inserir colaborador e cargo")    
    
@app.post("/AlterarColaboradorComCargo/", tags=["Colaboradores"])
def Alterar_Colaborador_Com_Cargo(
    
    colaborador: ColaboradorSchema.ColaboradorSchema,
    colaborador_cargo: ColaboradorCargoSchema.ColaboradorCargoSchema,
    user: dict = Depends(get_current_user)
):
    print('mainAlterar')
    dal = ColaboradorModel.ColaboradorDAL()
    resultado = dal.atualiza_colaborador_cargo(colaborador, colaborador_cargo)
    if resultado:
        return {"mensagem": "Colaborador e cargo atualizado com sucesso!"}
    else:
        raise HTTPException(status_code=400, detail="Erro ao inserir colaborador e cargo")    
