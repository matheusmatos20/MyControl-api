from pathlib import Path
from typing import Annotated, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from Model import Representantes as Representante,Cliente as Cliente,Cargo as Cargo,Servico as Servico,Colaborador as Colaborador,Financeiro as Financeiro, Fornecedor as Fornecedor, Pagamento as Pagamento, Conn_DB as Conn    
from Schemas import Representante as RepresentanteSchena,Cliente as ClienteSchema, Cargo as CargoSchema, Servico as ServicoSchema, Colaborador as ColaboradorSchema, ServicoCliente as ServicoClienteSchema, Fornecedor as FornecedorSchema, Pagamento as PagamentoSchema, NotaFiscalAviso as NotaFiscalAvisoSchema   
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import FastAPI
from Services.email_service import send_nf_notification, EmailDispatchError
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Configurações CORS
origins = [
    "http://localhost:5501",
    "http://mycontrol-frontend.s3-website-us-east-1.amazonaws.com"

]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    

@app.get("/keepalive")
async def keepalive():
    """Simple endpoint used for uptime checks."""
    return "API operacional"

# Configurações JWT
SECRET_KEY = "e7dff6e4a8c2b1f1a3b5e07b469dcd748ac4f3deab9b89c0c1a7f6db2a43f27c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Autenticação usando banco
# def authenticate_user(username: str, password: str):
#     conn = Conn()
#     user = conn.get_usuario(username, password=None)  # Busca usuário pelo login
#     if not user:
#         return False
#     hashed_password = user.get("DS_SENHA") or user.get("senha")  # Ajuste conforme sua coluna
#     if not pwd_context.verify(password, hashed_password):
#         return False
#     return {"username": user["NM_LOGIN"]}

def authenticate_user(username: str, password: str):
    try:
        conn = Conn.Conn()
        user = conn.get_usuario(username)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    if not user:
        return False

    # Converta para str simples
    hashed_password = str(user["DS_SENHA"])

    print("Senha fornecida:", repr(password))
    print("Hash do banco:", repr(hashed_password))

    if not pwd_context.verify(password, hashed_password):
        print("Senha inválida")
        return False

    return {"username": user["NM_LOGIN"], "empresa": user["EMPRESA"]}


# Criar token JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def _resolver_competencia(mes: Optional[int] = None, ano: Optional[int] = None, competencia: Optional[int] = None) -> Optional[int]:
    if competencia is not None:
        try:
            comp_int = int(competencia)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Competência inválida. Use o formato YYYYMM.")
        if comp_int < 190001 or comp_int > 999912:
            raise HTTPException(status_code=400, detail="Competência fora do intervalo permitido.")
        return comp_int
    if mes is not None or ano is not None:
        if mes is None or ano is None:
            raise HTTPException(status_code=400, detail="Informe mês e ano juntos.")
        try:
            mes_int = int(mes)
            ano_int = int(ano)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Mês e ano devem ser numéricos.")
        if mes_int < 1 or mes_int > 12:
            raise HTTPException(status_code=400, detail="Mês deve estar entre 1 e 12.")
        return int(f"{ano_int:04d}{mes_int:02d}")
    return None


# Função para obter usuário atual a partir do token
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return {"username": username}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Endpoint para login
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais incorretas")

    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"success": True, "token": access_token
            , "empresa": user["empresa"]
            , "usuario": user["username"]}

# ---------------------
# Endpoints protegidos 
# ---------------------
@app.post("/InserirDebito",tags=["Financeiro"])
async def Consultar_Debitos(pagamento:PagamentoSchema.PagamentoSchema ,current_user: dict = Depends(get_current_user)):
    try:

        print("entrou no inserir debito")
        dal = Pagamento.PagamentoDAL()
        df = dal.inserir_pagamento(pagamento)
        return {"mensagem": "Débito inserido com sucesso!"}
    except Exception as e:
        return {"erro": f"Erro ao inserir débito: {str(e)}"}

@app.post("/AvisoNotaFiscal",tags=["Financeiro"])
async def Aviso_NotaFiscal(aviso: NotaFiscalAvisoSchema.NotaFiscalAvisoSchema):
    dal = Pagamento.PagamentoDAL()
    print(aviso.cnpj_fornecedor)
    fornecedor = dal.obter_fornecedor_por_cnpj(aviso.cnpj_fornecedor)
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado para o CNPJ informado.")
    empresa = dal.obter_empresa_por_cnpj(aviso.cnpj_empresa)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada para o CNPJ informado.")

    id_usuario_padrao = 1

    try:
        sucesso = dal.registrar_aviso_nf(
            id_usuario=id_usuario_padrao,
            fornecedor=fornecedor,
            empresa=empresa,
            valor=aviso.valor,
            data_emissao=aviso.data_emissao,
            data_vencimento=aviso.data_vencimento,
            numero_nf=aviso.numero_nf,
            serie_nf=aviso.serie_nf,
            chave_nf=aviso.chave_nf,
            observacao=aviso.observacao
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha ao registrar aviso de nota fiscal: {exc}")

    if not sucesso:
        raise HTTPException(status_code=500, detail="Não foi possível registrar o aviso de nota fiscal.")

    email_enviado = False
    try:
        send_nf_notification(aviso, fornecedor, empresa)
        email_enviado = True
    except EmailDispatchError as exc:
        print(f"Falha ao enviar e-mail de aviso de NF: {exc}")

    return {
        "mensagem": "Aviso de nota fiscal registrado com sucesso!",
        "dados": {
            "fornecedor": fornecedor.get("NM_FANTASIA"),
            "empresa": empresa.get("NM_FANTASIA"),
            "valor": float(aviso.valor),
            "data_emissao": aviso.data_emissao.isoformat(),
            "data_vencimento": aviso.data_vencimento.isoformat(),
            "numero_nf": aviso.numero_nf,
            "serie_nf": aviso.serie_nf,
            "chave_nf": aviso.chave_nf,
        },
        "email_enviado": email_enviado
    }
@app.post("/BaixarDebito",tags=["Financeiro"])
async def Baixar_Debitos(id_pagamento,id_usuario ,current_user: dict = Depends(get_current_user)):
    try:
        print(id_pagamento)
        dal = Pagamento.PagamentoDAL()
        df = dal.baixar_pagamento(id_pagamento,id_usuario)
        return {"mensagem": "Débito baixado com sucesso!"}
    except Exception as e:
        return {"erro": f"Erro ao inserir débito: {str(e)}"}

@app.delete("/ExcluirDebito/{id_pagamento}",tags=["Financeiro"])
async def Excluir_Debito(id_pagamento: int, current_user: dict = Depends(get_current_user)):
    dal = Pagamento.PagamentoDAL()
    removido = dal.delete_pagamento(id_pagamento)
    if not removido:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado.")
    return {"mensagem": "Pagamento excluído com sucesso!", "id_pagamento": id_pagamento}

@app.get("/ListarDebitos",tags=["Financeiro"])
async def Listar_Debitos(current_user: dict = Depends(get_current_user)):
    dal = Pagamento.PagamentoDAL()
    df = dal.listar_debitos()
    return df.to_dict(orient="records")

@app.get("/ListarDebitosEmAberto",tags=["Financeiro"])
async def Listar_Debitos(current_user: dict = Depends(get_current_user)):
    dal = Pagamento.PagamentoDAL()
    df = dal.listar_debitos_em_aberto()
    return df.to_dict(orient="records")

@app.get("/RetornaDebito",tags=["Financeiro"])
async def Consultar_Debitos(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    competencia: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    filtro_competencia = _resolver_competencia(mes, ano, competencia)
    dal = Financeiro.FinanceiroDAL()
    df = dal.retorna_pagamentos(filtro_competencia)
    return df.to_dict(orient="records")

@app.get("/RetornaCredito",tags=["Financeiro"])
async def Consultar_Creditos(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    competencia: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    filtro_competencia = _resolver_competencia(mes, ano, competencia)
    dal = Financeiro.FinanceiroDAL()
    df = dal.retorna_creditos(filtro_competencia)
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



@app.post("/AlterarFornecedor/",tags=["Fornecedores"])
def Alterar_Fornecedor(fornecedor: FornecedorSchema.FornecedorSchema, user: dict = Depends(get_current_user)):
    try:
        dal = Fornecedor.FornecedorDAL()
        atualizado = dal.alterar_fornecedor(fornecedor)
        if not atualizado:
            raise HTTPException(status_code=404, detail="Fornecedor não encontrado.")
        return {
            "mensagem": "Fornecedor alterado com sucesso!",
            "dados": {
                "id_fornecedor": fornecedor.id_fornecedor,
                "nm_razao_social": fornecedor.nm_razao_social,
                "nm_fantasia": fornecedor.nm_fantasia,
                "cd_cnpj": fornecedor.cd_cnpj,
                "ds_endereco": fornecedor.ds_endereco,
                "nu_telefone": fornecedor.nu_telefone
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao alterar fornecedor: {str(e)}")


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

@app.get("/CargosColaborador",tags=["ColaboradoresCargos"])
async def Consultar_Colaborador_Cargos(current_user: dict = Depends(get_current_user), id_funcionario: int = None):
    dal = ColaboradorCargoModel.ColaboradorCargoDAL()
    df = dal.retorna_cargo_colaborador(id_funcionario)
    return df.to_dict(orient="records")



@app.post("/InserirColaboradorCargo/",tags=["ColaboradoresCargos"])
def Inserir_Colaborador_Cargo(cargo: ColaboradorCargoSchema.ColaboradorCargoSchema, user: dict = Depends(get_current_user)):
    try:
        dal = ColaboradorCargoModel.ColaboradorCargoDAL()
        resp = dal.inserir_cargo_colaborador(cargo)
        print(resp)
        if(resp):

            return {
                "mensagem": "Cargo de colaborador inserido com sucesso!",
                "dados": cargo.dict()
            }
        else:
            return {"erro": "Falha ao inserir cargo do colaborador."}
        
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









