# Árvore de decomposição

## Hierarquia
```
EPIC        → objetivo de negócio (semanas/meses)
  FEATURE   → capacidade entregável (dias/semana)
    STORY   → incremento de valor testável (horas/dias)
      TASK  → unidade de implementação (< 4h)
        SUB → subtarefa (< 2h), só quando a tarefa for ambígua
```

## Template por nível
```markdown
## [EPIC|FEAT|STORY|TASK]-NNN: <título>

Tipo: Epic | Feature | Story | Task
Status: Pendente | Em progresso | Implementado | Verificado | Reprovado
Estimativa: S(<4h) | M(4h–2d) | L(2–5d) | XL(>5d → DECOMPOR)
Prioridade: P0 (bloqueante) | P1 (must) | P2 (should) | P3 (nice)

Descrição
Como <papel>, quero <ação> para que <benefício>.

Critério de aceite
- [ ] CA-NNN-1: <verificável, caminho feliz>
- [ ] CA-NNN-2: <verificável, erro>
- [ ] CA-NNN-3: <NFR, se aplicável>

Dependências: <EPIC/FEAT/STORY ou "nenhuma">
Riscos: <risco ou "nenhum identificado">
Notas: <contexto, ADR>
```

## Regra XL
Item com estimativa **XL não pode ser delegado** sem decomposição. Bloquear handoff de XL — é o erro que
gera "entregou metade e disse que estava pronto".

## INVEST para story
| Letra | Critério |
|---|---|
| **I**ndependent | pode ser feita sem esperar outra story (ou dependência declarada) |
| **N**egotiable | escopo conversável, não contrato rígido de implementação |
| **V**aluable | entrega valor a um ator concreto |
| **E**stimable | dá para estimar com premissa declarada |
| **S**mall | cabe em dias, não em semanas |
| **T**estable | tem critério verificável |

Story que falha em 3+ letras volta para o refinamento.

## Tarefa boa
- Um objetivo, um resultado verificável.
- Arquivos alvo declarados (`src/services/order.ts`).
- Escopo exato: o que fazer **e o que não fazer**.
- Comando de verificação (`pnpm test:unit order`, `curl` de contrato).
- Estimativa ≤ 4h. Acima, quebre.

## Ligação com fatias
Fatia vertical é o **corte de entrega** (valor ponta a ponta); a árvore é o **corte de planejamento**
(epic → task). Uma fatia contém uma ou mais stories; uma story não atravessa fatias.

## Saída
`BACKLOG.yaml`/`BACKLOG.md` com a árvore, cada story com CA, cada task com arquivos e comando, e a lista de
XL pendentes de decomposição.
