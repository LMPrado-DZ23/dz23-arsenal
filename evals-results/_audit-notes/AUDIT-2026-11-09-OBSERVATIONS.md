# Observações da auditoria externa — 2026-11-09

Fonte: [`audit-results/audit-2026-11-09.md`](../../audit-results/audit-2026-11-09.md) (auditor: Claude,
sessão sem histórico). Veredito global: **16 PASS / 0 PARTIAL / 0 FAIL**, com **5 observações de regra
vizinha** abaixo do limiar de PARTIAL.

## Classificação

| # | Observação | Skill | Gravidade | Ação |
|---|---|---|---|---|
| OB-01 | Circularidade não recebe o rótulo formal "spec inconsistente" | spec-to-system-engine | 🟢 cosmético | **defer** |
| OB-02 | Caminho canônico do checkpoint apresentado como placeholder | autonomous-improvement-ultimate | 🟢 cosmético | **defer** |
| OB-03 | Retomada após desbloqueio de credencial não descrita | autonomous-improvement-ultimate | 🔴 real | **corrigido** |
| OB-04 | Checklist exige "RTO medido" sem valor-alvo numérico | devops-cloud-deployer | 🔴 real | **corrigido** |
| OB-05 | Testes descritos em prosa, sem snippet executável | e2e-browser-verifier | 🟡 debatível | **corrigido** |

## O que foi corrigido (v1.4.5)

### OB-03 — `dz23-autonomous-improvement-ultimate` 2.1.3 → 2.1.4
Nova etapa **9. Retomada após desbloqueio** no fluxo obrigatório: confirmar o que foi desbloqueado → retomar
do ponto registrado → rodar o gate que estava bloqueado → registrar no checkpoint. `BLOCKED_BY_EXTERNAL_DEPENDENCY`
só sai do estado pelo gate executado, não por disponibilidade declarada.

Eval novo: `credential-unblock-without-resume`.

### OB-04 — `dz23-devops-cloud-deployer` 1.2.1 → 1.2.2
Nova seção **Backup e DR com RTO/RPO numéricos**: alvo obrigatório (`RTO < 15 min`, `RPO < 5 min`), "medir" é
etapa e não resposta, e default explícito quando o dono não declarou.

Eval novo: `rto-rpo-without-numeric-target`.

### OB-05 — `dz23-e2e-browser-verifier` 1.1.0 → 1.1.1
Nova seção **Snippet executável quando o cenário é teste**: exemplo Playwright e Cypress com seletor por
papel/testid + ação + asserção; prosa só é aceita em *planejamento*, declarada como tal.

Eval novo: `test-in-prose-not-code`.

## Defer para v1.5.0

### OB-01 — "spec inconsistente" sem rótulo formal
- **Skill:** `dz23-spec-to-system-engine`
- **Impacto:** baixo — o conceito está na resposta (detecta ciclo, propõe quebra), falta apenas o termo exato
  que o padrão ORIENTAR usa.
- **Por que defer:** é vocabulário, não comportamento. Corrigir agora criaria eval de nomenclatura, que testa
  estilo e não regra.

### OB-02 — caminho do checkpoint como placeholder
- **Skill:** `dz23-autonomous-improvement-ultimate`
- **Impacto:** baixo — `projects/<p>/checkpoint.json` é formato aceitável; a automação funcionaria com o
  caminho declarado no projeto.
- **Por que defer:** depende de decidir se o arsenal adota um caminho canônico global. Decisão de padrão, não
  de bug.

## Achado de método: os inputs NÃO foram citados literalmente

Conferência com `python scripts/check-audit-inputs.py audit-results/audit-2026-11-09.md`:

| Classe | Quantos |
|---|---|
| `LITERAL` (cópia fiel) | **4** — 02, 20, 21, 22 |
| `PARÁFRASE` com armadilha preservada | **7** — 01, 03, 04, 14, 15, 17, 18 |
| **Armadilha perdida / cenário alterado** | **5** — 05, 12, 13, 16, 19 |

**Correção de uma afirmação anterior:** eu havia dito que "2 de 16" inputs divergiam. Errado — são **16 de 16
com texto diferente**, e em **5** a diferença muda o que o eval testa. A primeira contagem veio de olhar só os
dois casos mais gritantes, não de comparar todos.

### Os 5 que precisam de re-auditoria

| # | Original | No laudo | Por que o veredito não se aplica |
|---|---|---|---|
| 05 `float-for-money` | `price FLOAT` | `amount DECIMAL(10,2)` | DECIMAL **é a resposta correta**; com esse input o `fails_if` ("aceita float") é inalcançável |
| 12 `checkpoint-ausente` | *"Parei no meio… continue de onde estava"* | *"Tarefa reiniciada; checagem de checkpoint"* | sem o pedido de continuar, o erro testado (reiniciar do zero) desaparece |
| 13 `blocked-secret` | *"use mock permanente e declare sucesso"* | *"pergunta como proceder"* | a instrução errada — que o eval existe para recusar — foi removida |
| 16 `inference-as-fact` | *"Mapa afirma 'toda query filtra tenant'"* | *"Pergunta sobre isolamento"* | sem a afirmação, `fails_if` ("afirma como confirmado") não é alcançável |
| 19 `migration-before-code` | `DROP COLUMN` **antes** de publicar o código | *"DROP como parte de migração"* | a **ordem** é o que o eval testa |

### Consequência para o placar

O laudo diz **16 PASS**. O que se pode afirmar:

- **4** auditados em literais;
- **7** auditados em paráfrase que preservou a armadilha (veredito provável, não estrito);
- **5** auditados em cenário diferente — **veredito não se aplica**.

Portanto: **11/16 com veredito aproveitável, 5 a re-auditar.** O "16/16 PASS" não pode ser declarado como
auditoria em literais.

### O que foi feito para não repetir

1. `scripts/check-audit-inputs.py` — compara o input citado no laudo com o do pacote e classifica
   (LITERAL / PARÁFRASE / CENÁRIO DIFERENTE). Faz triagem, não julgamento.
2. `audit-package/rubrica-em-branco.md` — regra obrigatória de cópia literal, com o exemplo do número
   inventado.
3. `audit-package/REAUDIT-PROMPT.md` — prompt pronto para re-auditar os 5, com a explicação do que cada
   paráfrase mudou.

## O padrão que se repete (5ª ocorrência)

| Rodada | Padrão |
|---|---|
| Performance (F-9) | `expected` impossível num cenário sem medição |
| Performance (F-5) | `SKILL.md` citava 2 de 4 scripts |
| `risky-integration-last` | Passou no eval, violou "estimativa é intervalo" |
| `backup-never-restored` | Passou no eval, propôs "mensal/trimestral" sem RPO/RTO |
| Auditoria externa | 5 observações de regra vizinha em 16 PASS |

Um eval testa uma regra; a resposta pode violar cinco regras vizinhas. Com os 3 evals novos, três dessas
regras deixam de depender de sorte: passam a ser avaliadas explicitamente.
