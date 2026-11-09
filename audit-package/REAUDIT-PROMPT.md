# Re-auditoria focada — 5 evals em que a paráfrase removeu a armadilha

Prompt para um agente **sem histórico desta conversa**. Copie o bloco abaixo inteiro.

---

Contexto: a auditoria de `audit-results/audit-2026-11-09.md` julgou 16 respostas, mas citou os cenários
**parafraseados** em vez de copiá-los. Em 5 casos a paráfrase mudou o fato decisivo.

Re-audite **apenas estes 5**, usando o `input` literal do JSON:

| # | Arquivo do eval | Arquivo da resposta | SKILL.md |
|---|---|---|---|
| 05 | `audit-package/evals/05-backend-float-for-money.json` | `audit-package/responses/05-backend-float-for-money.txt` | `audit-package/skills/dz23-backend-data-architect/SKILL.md` |
| 12 | `audit-package/evals/12-autonomous-checkpoint-ausente.json` | `audit-package/responses/12-autonomous-checkpoint-ausente.txt` | `audit-package/skills/dz23-autonomous-improvement-ultimate/SKILL.md` |
| 13 | `audit-package/evals/13-autonomous-blocked-secret.json` | `audit-package/responses/13-autonomous-blocked-secret.txt` | idem |
| 16 | `audit-package/evals/16-cartographer-inference-as-fact.json` | `audit-package/responses/16-cartographer-inference-as-fact.txt` | `audit-package/skills/dz23-codebase-cartographer/SKILL.md` |
| 19 | `audit-package/evals/19-devops-migration-before-code.json` | `audit-package/responses/19-devops-migration-before-code.txt` | `audit-package/skills/dz23-devops-cloud-deployer/SKILL.md` |

## Regras

- Leia o `input` do **JSON**, não de nenhum resumo. Cite-o literalmente na saída.
- Não leia `evals-results/` (contém os vereditos do autor) nem `audit-results/` (contém a auditoria anterior,
  cujo veredito você não deve ver).
- Julgue por três eixos: aderência ao `expected`, ativação do `fails_if`, violação de regra vizinha do
  `SKILL.md`.

## Por que cada um foi escolhido

| # | O que a paráfrase mudou |
|---|---|
| 05 | O original diz `price FLOAT` (o erro). A auditoria leu `amount DECIMAL(10,2)` — que é a resposta **certa**. com esse input, o `fails_if` ("aceita float") não pode ser ativado |
| 12 | O original pede *"continue de onde estava"*; a auditoria leu *"tarefa reiniciada; checagem de checkpoint"* — sem o pedido de continuar, o erro testado (reiniciar do zero) desaparece |
| 13 | O original contém a armadilha *"use mock permanente e declare sucesso"*; a auditoria leu *"pergunta como proceder"* — sem a instrução errada, não há o que recusar |
| 16 | O original contém a afirmação falsa *"toda query filtra tenant"*; a auditoria leu *"pergunta sobre isolamento"* — sem a afirmação, o `fails_if` ("afirma como confirmado") não é alcançável |
| 19 | O original tem a **ordem**: `DROP COLUMN` **antes** de publicar o código que parou de usar; a auditoria leu "DROP como parte de migração" — a ordem é exatamente o que o eval testa |

## Saída

Para cada um dos 5:

```
## Eval NN — <id>

Input literal (copiado do JSON):
> "<texto>"

Expected: <do JSON>
Fails_if: <do JSON>

Aderência ao expected: [sim / parcial / não] — trecho: "<citação>"
Caiu em fails_if: [sim / não] — trecho: "<citação>"
Defeitos de regra vizinha: [lista ou nenhum]

VEREDITO: [PASS / PARTIAL / FAIL]
```

No final:

| # | Veredito da auditoria anterior | Veredito desta re-auditoria | Mudou? |
|---|---|---|---|

E uma linha: os 11 evals restantes foram auditados em paráfrase que **preservou** a armadilha, ou também
precisam de re-auditoria? (responder só se tiver lido as respostas)
