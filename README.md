# MyControl API

Back-end FastAPI com integrações para gestão (Clientes, Colaboradores, Serviços, Financeiro) e módulo de Escala de Serviço.

## Requisitos

- Python 3.10+
- SQL Server (com driver ODBC 17/18 instalado)
- Pip + venv
- (Opcional) Docker/Docker Compose

## Variáveis de Ambiente (SQL Server)

- `SQLSERVER_HOST` (ex: `mfmatos_grantempo.sqlserver.dbaas.com.br`)
- `SQLSERVER_DATABASE`
- `SQLSERVER_USER`
- `SQLSERVER_PASSWORD`
- (Opcional) `SQLSERVER_ODBC_DRIVER` (ex: `ODBC Driver 18 for SQL Server`)

O código autodetecta drivers; se precisar, force via `SQLSERVER_ODBC_DRIVER`.

## Instalação

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell
pip install -r app/requirements.txt
```

## Banco de Dados

1) Execute o script de estrutura/migrações: `database_changes.sql` no seu SQL Server.
2) Garanta que as tabelas base (ex.: TB_FUNCIONARIOS, TB_CARGOS, etc.) já existam no seu banco.

Novas tabelas para Escala:
- `TB_CARGA_HORARIA (ID, DS_CARGA_HORARIA, QT_HORAS_SEMANAIS)`
- `TB_POSTOS (ID_POSTO, NM_POSTO, ID_CARGA_HORARIA, QT_COLABORADORES)`
- `TB_ESCALA (ID_ESCALA, ID_FUNCIONARIO, ID_POSTO, DATA, TURNO, OBSERVACAO, DT_CADASTRO)`
- `TB_FOLGAS_FUNCIONARIO (ID_FOLGA, ID_FUNCIONARIO, DATA, OBSERVACAO, DT_CADASTRO)`

## Executando a API (dev)

```bash
uvicorn app.main:app --reload --port 8001
```

- O front padrão usa `app/Views/config.js` (API_BASE_URL). Por padrão aponta para `http://127.0.0.1:8001`.
- O Auth usa `app/Views/auth.js`; por padrão herda o mesmo host via `buildAuthUrl`.

CORS permitido em `app/main.py`:
- `http://localhost:5501`
- `http://mycontrol-frontend.s3-website-us-east-1.amazonaws.com`

Ajuste a lista `origins` conforme seu ambiente.

## Autenticação

- Endpoint de login: `POST /token` (OAuth2 Password)
- Envie `username` e `password` (form-urlencoded). Recebe `{ success, token, empresa, usuario }`.
- As views usam `localStorage` para token e renovação automática (ver `app/Views/auth.js`).

## Módulo Escala de Serviço (novo)

Principais endpoints:
- `POST /carga-horaria` — cadastra carga horária
- `GET /carga-horaria` — lista cargas horárias
- `POST /postos` — cadastra posto (vincula carga e quantidade)
- `GET /postos` — lista postos
- `PUT /postos/{id}` — atualiza posto
- `DELETE /postos/{id}` — remove posto
- `POST /escala/gerar` — gera escala automática por período/postos/cargos
- `GET /escala/funcionario/{id}` — consulta escala por colaborador
- `GET /escala/posto/{id_post}/data/{data}` — consulta por posto/dia
- `POST /escala` — insere item (alocação manual)
- `PUT /escala/{id}` — edita item
- `DELETE /escala/{id}` — exclui item
- `POST /escala/folga` — registra folga
- `GET /escala/folgas/funcionario/{id}` — lista folgas
- `DELETE /escala/folga/{id}` — exclui folga

View do módulo:
- `app/Views_Escala/Escala.html` (usa `Escala.js`/`Escala.css`)
- Integra-se ao menu e é responsiva (acompanha o recolher/expandir).

## Anotações Importantes

- Drivers ODBC: Instale `ODBC Driver 18 for SQL Server` (ou 17) no host de execução.
- Secrets: Altere `SECRET_KEY` em `app/main.py` para produção.
- CORS: Ajuste `origins` conforme seus domínios do front.
- Segurança: Senhas do banco via variáveis de ambiente (não comitar credenciais reais).
- Geração de escala: respeita folgas e quantidade por posto; 12x36 alterna dias.

## Estrutura

- `app/main.py` — FastAPI + rotas
- `app/Model/` — DALs (SQL Server via pyodbc)
- `app/Schemas/` — Pydantic Schemas
- `app/Views/` e `app/Views_Escala/` — Front (HTML/CSS/JS)
- `database_changes.sql` — DDL/migrações
- `docs/` — documentação técnica

## Documentação técnica

Veja `docs/` para lista completa de endpoints, fluxos e diagramas.
