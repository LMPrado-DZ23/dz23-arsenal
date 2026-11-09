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

## Achado de método (não estava na lista do auditor)

Conferindo os `input` citados no laudo contra `audit-package/evals/*.json`, **dois não batem literalmente**:

| Eval | Input no pacote | Input no laudo |
|---|---|---|
| 01 `conflicting-requirements` | `'Registrar tudo para auditoria' e 'não impactar latência em nenhum cenário'` | *"auditoria completa de todas as transações"* e *"latência < 100 ms por operação"* |
| 02 `circular-dependency` | `SL-02 depende de SL-03, que depende de SL-02` | *"Módulos A depende de B, B depende de C, C depende de A"* |

O auditor **parafraseou** (ou reconstruiu) o cenário em vez de copiar o literal. No caso 01 acrescentou um
número (`< 100 ms`) que **não existe** no input original.

**Consequência:** o veredito continua válido para o que o auditor leu — mas ele julgou um cenário
ligeiramente diferente do registrado. Para a próxima rodada: a rubrica deve exigir **cópia literal** do
`input`, e a auditoria deve declarar qualquer paráfrase.

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
