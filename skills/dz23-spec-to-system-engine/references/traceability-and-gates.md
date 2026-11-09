# Rastreabilidade e gates

## A cadeia que importa
```
REQ-NNN → fatia SL-XX → teste T-YY → evidência (saída/arquivo/demo) → estado
```
Requisito sem teste é requisito não coberto. Fatia sem `REQ` é trabalho órfão. Teste sem `REQ` pode ser
cobertura sem propósito — não é proibido, mas deve ser declarado.

## Matriz viva
`templates/req-matrix.md` é o artefato central. Ela é atualizada **a cada fatia entregue**, não no fim.
Se a matriz e o backlog divergem, a matriz está mentindo — corrija na hora.

## Estados
| Estado | Significa |
|---|---|
| `SPEC` | escrito, sem critério verificável |
| `READY` | critério verificável e prova definida |
| `IN_PROGRESS` | em execução |
| `DONE` | prova anexada e conferida |
| `CUT` | removido, com motivo e aprovador |
| `DEFERRED` | fora desta entrega, com data/gatilho |

## Gates da especificação
| Gate | PASS quando |
|---|---|
| Enquadramento | problema, atores, resultado, restrições e fora de escopo escritos |
| Requisitos | todo `REQ` tem origem, prioridade e critério verificável |
| Decomposição | toda fatia entrega valor de ponta a ponta, tem dono e DoD |
| Contratos | toda fronteira paralela tem contrato com erro/timeout e dono |
| Riscos | risco alto tem mitigação, dono e prazo; incerteza alta tem spike |
| Plano | caminho crítico identificado; estimativas com premissa; capacidade considerada |
| Rastreabilidade | matriz `REQ → fatia → teste → evidência` sem órfão |

## Revisão adversarial da spec
Pergunte, e responda por escrito:
1. Qual requisito eu **não** consigo provar hoje? (vira pergunta, não planilha)
2. Qual fatia não entrega valor sozinha? (é tarefa interna — reagrupar)
3. Qual dependência é circular? (o plano está errado)
4. Qual critério depende de opinião ("bonito", "rápido")? (reescrever)
5. O que acontece no caminho de erro/permissão? (se não está escrito, está faltando)
6. Onde o escopo pode crescer sem ninguém perceber? (declarar fora de escopo)

## Cadeia completa (com Gherkin)
```
REQ-001 → STORY-005 → feature/auth.feature:L12 → tests/auth.spec.ts:L45 → screenshots/reg.png → PASS
```

| REQ-ID | Descrição | Story | Cenário Gherkin | Teste automatizado | Evidência | Status |
|---|---|---|---|---|---|---|
| REQ-001 | cadastro de usuário | STORY-005 | `auth.feature:L12` | `auth.spec.ts:L45` | `screenshots/reg.png` | PASS |
| REQ-002 | login OAuth | STORY-006 | `auth.feature:L35` | `oauth.spec.ts:L10` | — | NOT_TESTED |

**Legenda:** `PASS` (implementado + teste + evidência) · `FAIL` (teste rodou e falhou) · `NOT_TESTED`
(implementado, sem teste executado) · `PENDENTE` (não implementado) · `BLOQUEADO` (depende de
`AMBIGUIDADE-XXX`) · `OUT_OF_SCOPE` (decisão com ADR).

> Os `REQ-XXX` emitidos aqui são os mesmos consumidos por `dz23-autonomous-improvement-ultimate` como
> critério de aceite do loop de correção. Se o ID muda, o loop perde a referência.

## Saída
Matriz preenchida, gates com estado, e a lista de perguntas abertas que **bloqueiam** execução.
