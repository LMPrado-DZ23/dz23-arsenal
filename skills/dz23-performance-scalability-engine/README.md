# DZ23 Performance & Scalability Engine v1.0.0

Skill de **plano cirúrgico de otimização de performance e escalabilidade** em 4 camadas, para DeepSeek
Harness e agentes compatíveis com `SKILL.md`.

Para cada um dos 20 itens: **problema que evita · como implementar na prática · diretriz técnica**.
Mede antes de otimizar, define budget, ataca o gargalo real e prova com antes/depois.

## As 4 camadas

| Camada | Itens |
|---|---|
| **1. Frontend & Interface** (UX e renderização) | skeleton loaders · mídia WebP/AVIF + lazy · code splitting e terceiros · virtualização de listas · debounce/throttle em input · fontes locais e cache · resiliência mobile |
| **2. Comunicação & Rede** (APIs e fluxos) | duplicidade e `Promise.all` · streaming de IA e UI otimista · timeout e resiliência · paginação/cursor |
| **3. Backend & Banco** (arquitetura) | N+1 · indexação composta · cache Redis · filas para trabalho pesado |
| **4. Infraestrutura & Deploy** (DevOps e observabilidade) | CDN · Brotli/GZIP · proximidade app↔banco · balanceamento de carga · OTel + RUM |

## Conteúdo

| Arquivo | Para quê |
|---|---|
| `SKILL.md` | Missão, workflow em 6 etapas, módulos 5.1–5.6, gates |
| `references/measurement-first.md` | Baseline por camada, percentis, sintético × RUM, k6, armadilhas |
| `references/perf-budget.md` | Tabelas de budget, priorização impacto ÷ esforço, custo |
| `references/frontend-layer.md` | Camada 1 — 7 itens com código real |
| `references/network-layer.md` | Camada 2 — 4 itens com código real |
| `references/backend-layer.md` | Camada 3 — 4 itens com SQL/ORM real |
| `references/infra-layer.md` | Camada 4 — 5 itens com config de proxy/CDN/OTel |
| `references/diagnostic-playbook.md` | Sintoma → camada → primeira medição; bisecção; árvore de decisão |
| `references/anti-patterns.md` | 49 erros recorrentes com correção |
| `references/quality-gates.md` | 9 gates, severidade e checklist |
| `references/installation.md` | Instalação, ferramental, quando não usar |
| `templates/perf-plan.md` | Plano com as 4 camadas × 20 itens + ordem de execução |
| `templates/layer-checklist.md` | Checklist dos 20 itens com estado e evidência |
| `templates/perf-budget.md` | Budget por métrica (vitals, bundle, API, banco, infra) |
| `templates/benchmark-report.md` | Antes/depois com configuração idêntica |
| `templates/diagnosis-report.md` | Baseline por camada + gargalo localizado + não medido |
| `templates/adr-performance.md` | ADR do trade-off, com medição e gatilho de revisão |
| `scripts/web_vitals_probe.py` | Sonda HTTP read-only: TTFB, bytes, compressão, cache, CDN |
| `scripts/compare_samples.py` | Percentis nearest-rank de duas amostras; bloqueia metadata divergente |
| `scripts/check_budget.py` | Parser budget × benchmark (não mede nada) |
| `scripts/validate_skill.py` | Validador do pacote |

## Escopo

**Diagnostica, planeja e mede.** A execução da mudança é da skill do domínio
(`dz23-backend-data-architect`, `dz23-ultimate-pro-max`, `dz23-devops-cloud-deployer`).
Micro-otimização antes do gargalo é proibida.

## Uso

1. Instalar em `~/.agents/skills/` (`references/installation.md`).
2. Invocar por `/dz23-performance-scalability-engine` ou por descrição ("está lento, diagnostique e corte").
3. Artefatos vão para `projects/<projeto>/perf/`.

```bash
python scripts/web_vitals_probe.py https://app.exemplo.com/          # TTFB, bytes, compressão, cache
python scripts/web_vitals_probe.py https://app.exemplo.com/ --runs 5 # p50/p95 de TTFB
python scripts/web_vitals_probe.py https://app.exemplo.com/ --json
```

**Prompt de ativação:** [`PROMPT-ATIVACAO.txt`](PROMPT-ATIVACAO.txt).
**Avaliação:** `evals/evals.json` — 15 cenários (schema 1). Cenários não são testes executados.
**Versão:** [`VERSION`](VERSION) (1.0.0) · histórico em [`CHANGELOG.md`](CHANGELOG.md).

## Princípio

Sem baseline, não há otimização — há opinião. Percentil, não média. Um gargalo por vez, na camada dele,
com prova antes/depois e guarda de regressão.

---

## Arsenal — resumo operacional

**Versão real (VERSION/frontmatter):** 1.3.0 · **Categoria:** performance · **Complexidade:** advanced

### Quando usar

- Investigar lentidão com medição real (LCP/INP, p50/p95/p99).
- Preparar sistema para pico de tráfego.
- Reduzir custo de infra com evidência.
- Corrigir N+1, índice ausente, bundle grande — sempre com prova.

### Quando NÃO usar

- Antes de existir baseline: a skill bloqueia otimização sem número.
- Micro-otimização antes de localizar o gargalo.
- Como checklist de boas práticas aplicada em tudo.

### Instalação

```bash
# Já incluída no install-all. Manual:
cp -r skills/dz23-performance-scalability-engine ~/.agents/skills/dz23-performance-scalability-engine
```

### Uso

```bash
/dz23-performance-scalability-engine

# ou por descrição — o agente carrega sozinho (ver SKILL.md)
```

### Pré-requisitos de CLI

`python`, `curl` (obrigatórias) · `lighthouse`, `k6`, `psql` (recomendadas — sem elas, load test e `EXPLAIN` ficam `BLOCKED`).

### Evidência / Quality gates

- Baseline medido com volume e percentil (nunca média).
- Budget declarado **antes** da mudança.
- Uma camada por vez, uma mudança por vez.
- Antes/depois com o mesmo instrumento, mesmo dado e mesmo ambiente.

### Integração com outras skills

Localiza o gargalo e delega: frontend → `dz23-ultimate-pro-max`, backend/banco → `dz23-backend-data-architect`, infra → `dz23-devops-cloud-deployer`.

### Versão e changelog

Ver [`CHANGELOG.md`](CHANGELOG.md) (desta skill) e o histórico do arsenal em [`../../CHANGELOG.md`](../../CHANGELOG.md).
