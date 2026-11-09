# TRACEABILITY — <projeto> — <data>

| REQ-ID | Descrição | Story | Cenário Gherkin | Teste automatizado | Evidência | Status |
|---|---|---|---|---|---|---|
| REQ-001 | | STORY-005 | `feature:x` | `spec.ts:Lx` | `screenshots/x.png` | PENDENTE |
| REQ-002 | | | | | | |

## Legenda
| Status | Significa |
|---|---|
| `PASS` | implementado + teste automatizado + evidência conferida |
| `FAIL` | teste rodou e falhou → bug no backlog |
| `NOT_TESTED` | implementado, sem teste executado nesta sessão |
| `PENDENTE` | não implementado |
| `BLOQUEADO` | depende de `AMBIGUIDADE-XXX` |
| `OUT_OF_SCOPE` | decidido não implementar — registrar ADR |

## Regras
- `REQ` sem linha aqui é requisito órfão: ou entra, ou é cortado com ADR.
- Os `REQ-XXX` são os mesmos consumidos por `dz23-autonomous-improvement-ultimate` como critério de aceite.
- `NOT_TESTED` nunca vira `PASS` por decurso de prazo.
- Matriz atualizada na mesma entrega, nunca "no fim".

## Resumo
- Total de `REQ`: __
- `PASS`: __ · `NOT_TESTED`: __ · `PENDENTE`: __ · `BLOQUEADO`: __ · `OUT_OF_SCOPE`: __
- Cobertura de prova: __%
