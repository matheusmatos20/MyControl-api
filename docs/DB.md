# Banco de Dados — Escala de Serviço

## Tabelas Novas

### TB_CARGA_HORARIA
- `ID_CARGA_HORARIA` INT IDENTITY PK
- `DS_CARGA_HORARIA` NVARCHAR(100) NOT NULL
- `QT_HORAS_SEMANAIS` INT NULL

### TB_POSTOS
- `ID_POSTO` INT IDENTITY PK
- `NM_POSTO` NVARCHAR(150) NOT NULL
- `ID_CARGA_HORARIA` INT NOT NULL — FK `TB_CARGA_HORARIA(ID_CARGA_HORARIA)`
- `QT_COLABORADORES` INT NOT NULL DEFAULT 1

### TB_ESCALA
- `ID_ESCALA` INT IDENTITY PK
- `ID_FUNCIONARIO` INT NOT NULL — FK `TB_FUNCIONARIOS(ID_FUNCIONARIO)`
- `ID_POSTO` INT NOT NULL — FK `TB_POSTOS(ID_POSTO)`
- `DATA` DATE NOT NULL
- `TURNO` NVARCHAR(50) NULL
- `OBSERVACAO` NVARCHAR(200) NULL
- `DT_CADASTRO` DATETIME NOT NULL DEFAULT GETDATE()

Índices e melhorias podem ser adicionados conforme necessidade de relatório/consulta.

### TB_FOLGAS_FUNCIONARIO
- `ID_FOLGA` INT IDENTITY PK
- `ID_FUNCIONARIO` INT NOT NULL — FK `TB_FUNCIONARIOS(ID_FUNCIONARIO)`
- `DATA` DATE NOT NULL
- `OBSERVACAO` NVARCHAR(200) NULL
- `DT_CADASTRO` DATETIME NOT NULL DEFAULT GETDATE()

## Regras
- Colaboradores devem estar ativos (sem `DT_DESLIGAMENTO`) — checado na geração via consulta do último cargo.
- Geração respeita `QT_COLABORADORES` do posto e as folgas no período.
- Carga `12x36`: alternância de alocações por paridade de dia/índice.

## Script de Criação
- Ver `database_changes.sql` para DDL completa e FKs condicionais.
