# Matriz de requisitos — <projeto>

Regra: `REQ` sem critério **não entra** em `READY`. `DONE` exige prova anexada.

| ID | Requisito | Origem | Prioridade | Critério verificável | Teste/Prova | Fatia | Estado |
|---|---|---|---|---|---|---|---|
| REQ-001 | | quem/quando | Must | observável e mensurável | T-01 / comando / demo | SL-01 | SPEC |
| REQ-002 | | | Should | | | | |

## Estados
`SPEC` → `READY` → `IN_PROGRESS` → `DONE` (prova) · `CUT` (motivo+aprovador) · `DEFERRED` (data/gatilho)

## Requisitos não funcionais
| ID | Categoria | Critério | Onde se aplica |
|---|---|---|---|
| NFR-001 | Latência | p95 ≤ ___ ms | rota crítica |
| NFR-002 | Volume | ___ registros / ___ req/s | função principal |
| NFR-003 | Disponibilidade | ___ % | serviço |
| NFR-004 | Acessibilidade | WCAG 2.2 AA | todas as telas do fluxo |
| NFR-005 | Segurança | autorização por recurso + tenant | dados de usuário |

## Conflitos e decisões
| Conflito | Decisão | Quem decidiu | Data |
|---|---|---|---|

## Requisitos cortados
| ID | Motivo | Aprovador | Para onde foi |
|---|---|---|---|

## Órfãos (trabalho sem requisito)
| Item | Por quê existe | Vira REQ? |
|---|---|---|
