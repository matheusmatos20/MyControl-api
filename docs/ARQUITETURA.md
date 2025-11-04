# Arquitetura e Fluxos

## Visão Geral

- Front-end (HTML/CSS/JS) em `app/Views/` e `app/Views_Escala/`
- Back-end FastAPI em `app/main.py`
- Acesso a dados via DALs em `app/Model/` (pyodbc + SQL Server)
- Esquemas de validação em `app/Schemas/`

## Diagrama (Mermaid)

```mermaid
graph TD
  subgraph Browser
    V1[Views\n      - Index/Home\n      - Clientes\n      - Colaboradores\n      - Serviços\n      - Escala]
    Menu[Menu Lateral]
  end

  V1 -->|fetch JSON| API[FastAPI app/main.py]
  Menu --> V1

  subgraph API Layer
    Routes[Rotas + Auth]
    Schemas[Pydantic Schemas]
  end

  API --> Routes
  Routes --> DAL[Model/* DALs]
  DAL --> DB[(SQL Server)]
```

## Fluxo de Escala (Geração)

```mermaid
sequenceDiagram
  participant UI as View_Escala
  participant API as FastAPI
  participant DAL as EscalaDAL
  participant DB as SQL Server

  UI->>API: POST /escala/gerar { período, id_postos?, id_cargos? }
  API->>DAL: gerar_escala(payload)
  DAL->>DB: SELECT postos, cargas, colaboradores (ativos)
  DAL->>DB: SELECT folgas no período
  DAL->>DAL: Algoritmo distribuição (round-robin, 12x36 alternância)
  DAL->>DB: INSERT TB_ESCALA (lote)
  DAL-->>API: itens gerados
  API-->>UI: { mensagem, itens }
```

## Fluxo de Edição por Célula

```mermaid
sequenceDiagram
  participant UI
  participant API
  participant DAL
  participant DB

  UI->>API: GET /escala/posto/{id}/data/{data}
  API->>DAL: consultar_escala_posto_dia
  DAL->>DB: SELECT ... TB_ESCALA JOIN TB_FUNCIONARIOS
  DAL-->>API: lista
  API-->>UI: lista

  UI->>API: POST /escala (se vazio) OU PUT /escala/{id}
  API->>DAL: inserir_escala_item / atualizar_escala_item
  DAL->>DB: INSERT/UPDATE TB_ESCALA
  API-->>UI: OK
```
