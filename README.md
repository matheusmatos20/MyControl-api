# MyControl API (Azure Functions)

Backend FastAPI hospedado dentro do Azure Functions (Python) para atender o MyControl.  
A mesma base FastAPI continua existindo em `app/main.py`, porém agora é exposta por um único HTTP Trigger que usa `AsgiMiddleware`.

## Visão geral da arquitetura

```
Azure Static Web Apps (front)  --->  https://<sua-func-app>.azurewebsites.net/api/*
                                                |
                                                v
                              Azure Functions (Python v4) + FastAPI (app/main.py)
                                                |
                                                v
                                      SQL Server (pyodbc)
```

- Todas as rotas REST existentes continuam localizadas em `app/main.py`.
- `function_app.py` cria a Function `FastAPIHost` e encaminha qualquer chamada (`{*segments}`) para o FastAPI via `AsgiMiddleware`.
- Para desenvolvimento local usamos Azure Functions Core Tools (`func start`) e o Azurite/Storage Emulator (`UseDevelopmentStorage=true` já funciona).

## Pré-requisitos

- Python 3.10+ (recomendado 3.11).
- [Azure Functions Core Tools v4](https://learn.microsoft.com/azure/azure-functions/functions-run-local).
- ODBC Driver 17 ou 18 para SQL Server (necessário ao `pyodbc`).
- SQL Server acessível com o schema do `database_changes.sql`.
- (Opcional) Azurite ou Storage Emulator — o `local.settings.json` já usa `UseDevelopmentStorage=true`.

### Variáveis de ambiente

Configure em `local.settings.json` (para dev) ou nas Application Settings (produção):

| Variável | Descrição |
| --- | --- |
| `SQLSERVER_HOST` | Host ou instancia do SQL Server (`server,port` ou FQDN). |
| `SQLSERVER_DATABASE` | Nome do database. |
| `SQLSERVER_USER` / `SQLSERVER_PASSWORD` | Credenciais com acesso às tabelas da aplicação. |
| `SQLSERVER_ODBC_DRIVER` | Driver ODBC forçado (ex.: `ODBC Driver 18 for SQL Server`). Opcional; o código autodetecta. |
| `SECRET_KEY` | Chave usada para assinar os JWTs (troque em produção). |

> **Importante:** os valores em `local.settings.json` são placeholders. Ajuste antes de rodar localmente e **não** faça commit de segredos reais.

## Configuração local

```bash
python -m venv .venv
. .venv/Scripts/activate   # PowerShell
pip install -r requirements.txt
# Ajuste local.settings.json com o host/credenciais do SQL Server
func start
```

- O Functions Core Tools vai subir em `http://localhost:7071`.  
- As rotas ficam disponíveis sob `http://localhost:7071/api/...`.  
- Para que o front local use essa instância você pode temporariamente definir:

```html
<script>
  window.APP_CONFIG = { API_BASE_URL: 'http://localhost:7071/api' };
</script>
```

ou alterar `app/Views/config.js` enquanto estiver desenvolvendo.

### Debug/Standalone FastAPI (opcional)

Ainda é possível subir apenas o FastAPI:

```bash
uvicorn app.main:app --reload --port 8001
```

Isso é útil para debugging rápido, porém o fluxo oficial de deploy agora depende do Azure Functions.

## Estrutura do repositório

| Caminho | Descrição |
| --- | --- |
| `app/main.py` | FastAPI com todos os endpoints (clientes, colaboradores, serviços, pagamentos, escala, etc.). |
| `app/Model/` | Camada de acesso ao SQL Server (pyodbc). |
| `app/Schemas/` | Schemas Pydantic utilizados nas respostas/validações. |
| `app/Views/` | Front-end legado usado pelo time (HTML/CSS/JS). |
| `function_app.py` | Define o `FunctionApp` e expõe o FastAPI via `AsgiMiddleware`. |
| `local.settings.json` | Configurações locais (não vai para produção). |
| `host.json` | Configuração do host Azure Functions. |
| `requirements.txt` | Dependências Python (incluindo `azure-functions`). |
| `database_changes.sql` | Estrutura necessária no SQL Server. |
| `docs/` | Diagramas e documentos auxiliares. |

## Banco de dados

1. Execute `database_changes.sql` para criar/atualizar tabelas.
2. Verifique se as tabelas legadas (TB_FUNCIONARIOS, TB_CLIENTES, etc.) estão populadas.
3. A conexão é construída dinamicamente em `app/Model/Conn_DB.py` com base nas variáveis `SQLSERVER_*`.

## Fluxo principal / módulos

- **Autenticação**: `POST /token` (OAuth2 password). O front salva o JWT e o `auth.js` renova automaticamente.
- **Colaboradores / Clientes / Serviços / Pagamentos**: CRUD completo usando as tabelas já existentes.
- **Escala de Serviço**: Endpoint para cargas horárias, postos, geração automática e controle de folgas.
- **Keepalive**: `GET /keepalive` ajuda no monitoring.

Todos esses endpoints continuam com o mesmo path usado antes da migração; apenas o host muda para a Function App.

## Como testar

1. Suba o Functions local (`func start`).
2. Rode a suíte de testes/unitários customizados com `pytest` se necessário (`pytest app/tests` quando existirem).
3. Exercite os fluxos principais via `httpx` ou `curl`:

```bash
curl http://localhost:7071/api/keepalive
curl -X POST http://localhost:7071/api/token -d "username=...&password=..."
```

4. Abra as telas HTML em `app/Views` utilizando `Live Server`/`http.server` e garanta que `window.APP_CONFIG` aponta para `http://localhost:7071/api`.

## Deploy (resumo)

1. Empacote e envie o código para a Function App (`func azure functionapp publish <nome>` ou pipeline GitHub).  
2. Configure as Application Settings com os mesmos `SQLSERVER_*` e `SECRET_KEY`.  
3. Atualize o Static Web App (ou CDN) para consumir o novo host `https://<func>.azurewebsites.net/api`.  
4. Habilite logs em Application Insights para acompanhar execuções.

## Próximos passos

- Migrar secrets para Azure Key Vault quando estiver em produção.
- Adicionar testes automatizados para os módulos críticos (Pagamentos/Escala).
- Automatizar o deploy via GitHub Actions utilizando `azure-functions-action`.
