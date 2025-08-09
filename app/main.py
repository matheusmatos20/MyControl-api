from pathlib import Path
from typing import Annotated, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from Model import Curso as CursoDal
from Schemas import Curso as CursoSchema
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

app = FastAPI(
    title="Fast Api Fia",
    version="0.1.0",
    description="Minha api",
)

@app.get("/Cursos",tags=["Cursos"])
async def Consultar_Cursos():
    BancoDeDados = CursoDal.CursoDAL()
    retornoBancoDeDados = BancoDeDados.get_cursos()
    return retornoBancoDeDados.to_dict(orient='records')

@app.post("/InserirCurso",tags=["Cursos"])
async def Consultar_Cursos(curso: CursoSchema.CursoSchema):
    try:
        dt_criacao = datetime.strptime(curso.dt_criacao, "%d/%m/%Y").date()
        BancoDeDados = CursoDal.CursoDAL()
        BancoDeDados.InserirCurso(curso)
        
        return{
            "mensagem": "Curso Inserido com sucesso!",
            "dados": {
                "Curso": curso.nm_curso,
                "Descricao": curso.ds_curso
            }
        }
        
    except ValueError as e:
        return {"erro": f" {str(e)}"}