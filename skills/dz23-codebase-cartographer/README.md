# DZ23 Codebase Cartographer v1.0.0

Skill de **engenharia de contexto e mapeamento de codebase** para DeepSeek Harness e agentes compatíveis
com `SKILL.md`.

Transforma um repositório desconhecido em mapa verificável **antes** de qualquer mudança: topologia, entry
points, grafo real de dependências, fluxo de dados, convenções do repo, zonas de risco e dívida — e um
context brief enxuto, com ponteiros, para o próximo agente não reler mil arquivos.

## Conteúdo

| Arquivo | Para quê |
|---|---|
| `SKILL.md` | Missão com limites, workflow em 7 etapas, módulos 5.1–5.6 |
| `references/discovery-scan.md` | Topografia em 60s, manifests, CI, testes, git intelligence |
| `references/entrypoints-and-spine.md` | Backend/banco/frontend/workers: onde a execução começa |
| `references/dependency-graph.md` | Grafo real, ciclos, hubs, impacto ALTO/MÉDIO/BAIXO |
| `references/data-and-flow.md` | Fonte da verdade × cópias, os 5 saltos, escritor/leitor |
| `references/context-budget.md` | 3 fases de leitura, budget S/M/L, working set |
| `references/conventions-and-style.md` | Convenções do repo com exemplo real; invariantes |
| `references/hotspots-and-debt.md` | Churn × complexidade, código morto com prova, duplicação |
| `references/risk-zones.md` | Dinheiro, auth, migração, fila; blast radius; "não tocar" |
| `references/security-and-evidence.md` | Docs não confiáveis, estados de evidência, security mapping |
| `references/mapping-playbook.md` | Receituário ripgrep por tipo de achado e por stack |
| `references/context-brief.md` | Como escrever brief com orçamento e ponteiros |
| `references/verification-and-freshness.md` | Verificação por afirmação, validade, revalidação |
| `references/anti-patterns.md` | 30 erros recorrentes com correção |
| `references/quality-gates.md` | Gates e severidade + checklist |
| `references/installation.md` | Instalação, onde guardar artefatos, quando não usar |
| `templates/codebase-map.md` | Mapa com cabeçalho de commit/data e nível de confiança |
| `templates/EVIDENCE_LEDGER.md` | Ledger de afirmações com VERIFIED/INFERRED/UNKNOWN/BLOCKED |
| `templates/AGENT_HANDOFF.md` | Handoff: working set, limites, estado git, próximos passos |
| `templates/context-pack.md` | Prova do orçamento: 3 fases, custo real, não lido |
| `templates/context-brief.md` | Brief enxuto para agente |
| `templates/change-impact.md` | Impacto: importadores, rotas, tabelas, testes |
| `templates/hotspot-report.md` | Hot spots, código morto, dívida declarada e escondida |
| `scripts/repo_probe.py` | Scanner **read-only** do repo (texto ou `--json`) |
| `scripts/repo_inventory.py` | Inventário Git: **só metadata**, nunca conteúdo; exclui sensível |
| `scripts/validate_skill.py` | Validador do pacote |

## Escopo

**Lê e mapeia. Não altera código.** Não substitui `dz23-spec-to-system-engine` (o que construir),
`dz23-backend-data-architect` (mudança de backend), `architect` (decisão estrutural) nem `ponytail-audit`
(auditoria de qualidade). Ela produz o contexto que essas skills consomem.

## Uso

1. Instalar em `~/.agents/skills/` (`references/installation.md`).
2. Invocar por `/dz23-codebase-cartographer` ou por descrição ("mapeie este repositório com evidência").
3. Artefatos vão para `projects/<projeto>/map/`, não para a pasta da skill.

```bash
python scripts/repo_probe.py <path-do-repo>          # resumo
python scripts/repo_probe.py <path> --json           # JSON para o mapa
```

**Prompt de ativação:** [`PROMPT-ATIVACAO.txt`](PROMPT-ATIVACAO.txt).
**Avaliação:** `evals/evals.json` — 15 cenários (schema 1). Cenários não são testes executados.
**Versão:** [`VERSION`](VERSION) (1.0.0) · histórico em [`CHANGELOG.md`](CHANGELOG.md).

## Princípio

Mapa sem commit é passivo. Afirmação sem `arquivo:linha` é boato. Contexto sem ponteiro é resumo caro.

---

## Arsenal — resumo operacional

**Versão real (VERSION/frontmatter):** 1.1.0 · **Categoria:** exploration · **Complexidade:** intermediate

### Quando usar

- Entrar em repositório desconhecido (onboarding, primeiro dia).
- Antes de refactor em código legado.
- Avaliar impacto de mudança em módulo com muitas dependências.
- Quando o repo é grande demais para o agente ler inteiro.

### Quando NÃO usar

- Repo de 3 arquivos: ler direto é mais rápido.
- Quando o mapa já está atualizado.
- Análise de artefato compilado sem fonte (use `dz23-reverse-engineer-anything`).

### Instalação

```bash
# Já incluída no install-all. Manual:
cp -r skills/dz23-codebase-cartographer ~/.agents/skills/dz23-codebase-cartographer
```

### Uso

```bash
/dz23-codebase-cartographer

# ou por descrição — o agente carrega sozinho (ver SKILL.md)
```

### Pré-requisitos de CLI

`git`, `rg`, `python` (obrigatórias) · `jq` (recomendada) · `graphlint` (opcional, grafo de dependência).

### Evidência / Quality gates

- Toda afirmação com `arquivo:linha` ou comando executado.
- Zonas de risco declaradas: hot path, código sem teste, dependência circular.
- `EVIDENCE_LEDGER` separando verificado de `NOT_TESTED`.
- Handoff pronto: o brief é entrada para outra skill, não relatório de vaidade.

### Integração com outras skills

Alimenta `dz23-backend-data-architect` e `dz23-ultimate-pro-max` com contexto; precede qualquer mudança em legado; recebe dossiê de `dz23-reverse-engineer-anything`.

### Versão e changelog

Ver [`CHANGELOG.md`](CHANGELOG.md) (desta skill) e o histórico do arsenal em [`../../CHANGELOG.md`](../../CHANGELOG.md).
