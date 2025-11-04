# API — Endpoints Principais

Autenticação
- POST `/token` — autenticação OAuth2 Password. Body: `username`, `password` (form-urlencoded). Retorna `{ success, token, empresa, usuario }`.

Representantes
- GET `/Representantes`
- GET `/RepresentantesComboBox`
- POST `/InserirRepresentante/`
- POST `/AlterarRepresentante/`

Clientes
- GET `/Clientes`
- GET `/ClientesComboBox`
- POST `/InserirCliente/`
- POST `/AlterarCliente/`

Cargos
- GET `/Cargos`
- GET `/CargosComboBox`
- POST `/InserirCargo/`
- POST `/AlterarCargo/`

Serviços
- GET `/Servicos`
- GET `/ServicosComboBox`
- POST `/InserirServico/`
- POST `/AlterarServico/`
- POST `/InserirServicoCliente/`
- GET `/ServicosCliente`

Colaboradores
- GET `/Colaboradores`
- GET `/ColaboradoresComboBox`
- POST `/InserirColaborador/`
- POST `/AlterarColaborador/`

Financeiro / Pagamentos
- POST `/InserirDebito`
- POST `/BaixarDebito`
- DELETE `/ExcluirDebito/{id_pagamento}`
- GET `/ListarDebitos`
- GET `/ListarDebitosEmAberto`
- GET `/RetornaDebito`
- GET `/RetornaCredito`
- POST `/pagamentos/parcelado`
- GET `/pagamentos/parcelado/semana`

Nota Fiscal
- POST `/AvisoNotaFiscal`

Despesas Fixas
- POST `/despesas-fixas/processar`
- GET `/despesas-fixas/pendencias`
- POST `/despesas-fixas/confirmar`
- POST `/despesas-fixas/auto-confirmar`

Contas a Receber — Recorrentes
- POST `/contas-receber/recorrentes/processar`
- POST `/contas-receber/recorrentes/finalizar`

Dashboard
- GET `/dashboard/resumo`

Escala de Serviço (Novo)
- Carga horária
  - POST `/carga-horaria` — body: `{ ds_carga_horaria: string, qt_horas_semanais?: number }`
  - GET `/carga-horaria`
- Postos
  - POST `/postos` — body: `{ nm_posto: string, id_carga_horaria: number, qt_colaboradores: number }`
  - GET `/postos`
  - PUT `/postos/{id}` — body igual ao POST
  - DELETE `/postos/{id}`
- Escala automática e consulta
  - POST `/escala/gerar` — body: `{ periodo_inicio: 'YYYY-MM-DD', periodo_fim: 'YYYY-MM-DD', id_postos?: number[], id_cargos?: number[], limpar_existente?: boolean }`
  - GET `/escala/funcionario/{id_funcionario}`
  - GET `/escala/posto/{id_post}/data/{data}` (YYYY-MM-DD)
- Escala manual (edição por célula)
  - POST `/escala` — body: `{ id_funcionario: number, id_posto: number, data: 'YYYY-MM-DD', turno?: string, observacao?: string }`
  - PUT `/escala/{id}` — body igual ao POST
  - DELETE `/escala/{id}`
- Folgas
  - POST `/escala/folga` — body: `{ id_funcionario: number, data: 'YYYY-MM-DD', observacao?: string }`
  - GET `/escala/folgas/funcionario/{id_funcionario}`
  - DELETE `/escala/folga/{id_folga}`

# Observações de Autorização
- Todas as rotas (exceto `/token` e `/keepalive`) exigem Bearer Token.
- Header: `Authorization: Bearer <token>`.
