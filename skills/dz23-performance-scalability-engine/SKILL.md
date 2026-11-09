---
name: dz23-performance-scalability-engine
version: 1.3.0
description: >
  Plano cirúrgico de otimização de performance e escalabilidade em 4 camadas —
  Frontend/Interface (UX e renderização), Comunicação/Rede (APIs e fluxos),
  Backend/Banco (arquitetura) e Infraestrutura/Deploy (DevOps e observabilidade).
  Para cada item: problema que evita, como implementar na prática e diretriz
  técnica. Mede antes de otimizar, define budget, ataca o gargalo real e prova
  com antes/depois. Ative ao investigar lentidão, preparar pico, reduzir custo
  de infra, corrigir N+1, LCP/INP ruim ou escalar tráfego.
user-invocable: true
argument-hint: "<URL/rota/handler, 'diagnose <alvo>', 'plan <alvo>' ou 'audit <path>'>"
---

> v1.0 — medir, achar o gargalo, cortar na camada certa e provar com número.

# DZ23 PERFORMANCE & SCALABILITY ENGINE — v1.0

## Missão
Aja como engenheiro de performance sênior: transforme "está lento" em **plano cirúrgico por camada**, com baseline medido, gargalo localizado, mudança mínima de maior impacto e prova antes/depois. Performance não é lista de boas práticas aplicada em tudo — é **orçamento** (budget) defendido com medição. Otimizar sem medir é chute caro; medir sem budget é relatório.

**Limites:** esta skill **diagnostica, planeja e mede**; a mudança de código obedece à skill do domínio (`dz23-backend-data-architect`, `dz23-ultimate-pro-max`, `dz23-devops-cloud-deployer`). Micro-otimização antes do gargalo é proibida. Nenhum número sem instrumento: sem medição, o estado é `NOT_TESTED`.

## Regras de precedência
Correção e segurança > disponibilidade > integridade de dado > budget de performance > custo > preferência de framework > esta skill. Nunca troque correção por latência (cache de resultado errado, índice que quebra escrita, lazy load que esconde erro).

## Workflow obrigatório
MEDIR → LOCALIZAR → ORÇAR → CORTAR → VERIFICAR → GUARDAR.

1. **MEDIR** baseline real — não a sensação. RUM (p75 LCP/INP/CLS), latência p50/p95/p99 por rota, tempo de query, CPU/memória, custo. Leia `references/measurement-first.md`.
2. **LOCALIZAR** o gargalo na camada certa com evidência: trace, `EXPLAIN (ANALYZE, BUFFERS)`, flamegraph, waterfall de rede. Um gargalo por vez.
3. **ORÇAR** o alvo antes de mexer: budget por rota/endpoint (ex.: p75 LCP < 2,5 s; p95 API < 300 ms; query < 50 ms). Leia `references/perf-budget.md`.
4. **CORTAR** na camada do gargalo, na ordem de maior impacto ÷ esforço, com mudança mínima. Leia as 4 camadas (5.2–5.5).
5. **VERIFICAR** com a mesma medição do baseline; regressão de budget bloqueia o merge.
6. **GUARDAR** com gate automatizado (teste de carga no CI ou budget check) — performance sem guarda volta a degradar.

## Módulos de decisão (5.1–5.6)
   5.1 **Medição e baseline**: instrumento antes de opinião — RUM + sintético + perfil de servidor + plano de query. Percentil, não média. Leia `references/measurement-first.md` e `references/perf-budget.md`.
   5.2 **Camada 1 — Frontend & Interface (UX e renderização)**: skeleton loaders, mídia moderna (WebP/AVIF + lazy), code splitting e terceiros tardios, virtualização de listas, debounce/throttle em input, fontes locais com cache agressivo, resiliência mobile. Leia `references/frontend-layer.md`.
   5.3 **Camada 2 — Comunicação & Rede (APIs e fluxos)**: eliminar chamada duplicada, `Promise.all` para independentes, streaming de IA e UI otimista, timeout rígido em toda API externa, paginação/cursor em toda listagem pesada. Leia `references/network-layer.md`.
   5.4 **Camada 3 — Backend & Banco (arquitetura)**: N+1 com prova de query, índice composto pela consulta real, cache Redis com TTL e invalidação, fila para trabalho pesado. Leia `references/backend-layer.md`.
   5.5 **Camada 4 — Infraestrutura & Deploy (DevOps e observabilidade)**: CDN para estáticos, Brotli/GZIP, co-localização app↔banco, balanceamento entre instâncias, OpenTelemetry + RUM. Leia `references/infra-layer.md`.
   5.6 **Verificação e guarda de regressão**: mesmo instrumento do baseline, comparação honesta, gate no CI, alerta de SLO e o que fazer quando o budget estoura. Leia `references/quality-gates.md`.

## Padrões inegociáveis
- **Medir antes de otimizar**: baseline numérico ou `NOT_TESTED`. Sem número, não há otimização — há opinião.
- **Percentil, nunca média**: p50/p95/p99 (e p75 para vitals). Média esconde a cauda que o usuário sente.
- **Um gargalo por vez**: mudança e medição isoladas; duas mudanças juntas = nenhuma conclusão.
- **Budget declarado antes**: alvo por rota/endpoint; sem alvo, "melhorou" é indefinido.
- **Atacar a camada do gargalo**: cache no backend quando o problema é bundle no cliente é desperdício.
- **Nunca degradar correção**: cache de resultado errado, índice que trava escrita, lazy que esconde erro.
- **Prova antes/depois com o mesmo instrumento**: carga, dado e ambiente comparáveis; senão o ganho é fictício.
- **Guarda de regressão**: budget no CI ou alerta de SLO — senão a performance volta em silêncio.
- **Custo explícito**: toda otimização tem custo (memória, dinheiro, complexidade); declare.

## Pré-condições obrigatórias
```
ALVO:      [URL, endpoint, tabela ou componente]
BASELINE:  [valor atual medido — LCP, p95, query time]
THRESHOLD: [meta com unidade]
CAMADA:    [Frontend | Rede | Backend | Infra]
BLOQUEIOS: [dependências externas]
```
Baseline não medido → `BLOCKED_BY_EXTERNAL_DEPENDENCY`. Nunca preencher com estimativa.

**ALVO inferido deve ser marcado `(a confirmar)`.** Se o usuário não declarou qual rota/handler/serviço é o alvo, o agente **não** pode assumir. Exemplo:
```
ALVO: rota <não informada> (a confirmar com usuário)
```
Atribuir alvo ao pedido sem confirmação viola a regra de separar **observado** de **inferido** (§5.6). Escrever "rota /orders (do pedido)" quando o pedido não citou `/orders` é fabricação, não dedução.

**Pré-condições devem carregar o que está sendo proposto.** Se o agente vai propor um budget (ex.: p95 ≤ 300 ms), a linha `THRESHOLD:` deve dizer `proposta inicial: p95 ≤ 300 ms` — **não** `NÃO DECLARADO` com a proposta escondida em outra seção. Contradição interna entre seções é bug de execução, não detalhe de redação.

## As 4 camadas × 20 itens
| Camada | Item | Reference |
|---|---|---|
| Frontend | 1.1 Skeleton Loaders | `frontend-layer.md` §1.1 |
| Frontend | 1.2 Otimização de Mídia | `frontend-layer.md` §1.2 |
| Frontend | 1.3 Code Splitting & Bundling | `frontend-layer.md` §1.3 |
| Frontend | 1.4 Virtualização de Listas | `frontend-layer.md` §1.4 |
| Frontend | 1.5 Otimização de Input | `frontend-layer.md` §1.5 |
| Frontend | 1.6 Fontes & Estáticos | `frontend-layer.md` §1.6 |
| Frontend | 1.7 Resiliência Mobile | `frontend-layer.md` §1.7 |
| Rede | 2.1 Prevenção de Duplicidade | `network-layer.md` §2.1 |
| Rede | 2.2 Streaming & Otimização de IA | `network-layer.md` §2.2 |
| Rede | 2.3 Timeouts & Resiliência | `network-layer.md` §2.3 |
| Rede | 2.4 Paginação Eficiente | `network-layer.md` §2.4 |
| Backend | 3.1 Prevenção de N+1 | `backend-layer.md` §3.1 |
| Backend | 3.2 Indexação Estratégica | `backend-layer.md` §3.2 |
| Backend | 3.3 Camada de Cache (Redis) | `backend-layer.md` §3.3 |
| Backend | 3.4 Filas para Processamento Assíncrono | `backend-layer.md` §3.4 |
| Infra | 4.1 CDN & Distribuição de Ativos | `infra-layer.md` §4.1 |
| Infra | 4.2 Compressão de Tráfego | `infra-layer.md` §4.2 |
| Infra | 4.3 Proximidade Geográfica | `infra-layer.md` §4.3 |
| Infra | 4.4 Balanceamento de Carga | `infra-layer.md` §4.4 |
| Infra | 4.5 Monitoramento & RUM | `infra-layer.md` §4.5 |

Item 3.4: a spec original dizia "Filas para Processamento **Assalariado**" (typo) — interpretado como
processamento **assíncrono** em filas/workers. O original está preservado em `_sources/user-spec.md` e a
correção está anotada em comentário HTML no topo de `backend-layer.md`.

## Entregáveis obrigatórios
| Artefato | Caminho |
|---|---|
| `diagnosis-report.md` | `projects/<p>/perf/diagnosis-report.md` |
| `optimization-plan.md` | `projects/<p>/perf/optimization-plan.md` |
| `benchmark-comparison.md` | `projects/<p>/perf/benchmark-comparison.md` |
| `performance-budget.md` | `projects/<p>/perf/performance-budget.md` |
| `adr-performance.md` | `projects/<p>/perf/adr/ADR-NNN.md` |

## Guardrails de segurança
- **Nunca** rodar load test em produção sem autorização explícita.
- `Promise.all` **paraleliza, não deduplica** — use cache/in-flight por chave.
- **Optimistic UI só para operação reversível**; nunca confirmação falsa em dinheiro/permissão.
- **Cache keys isoladas por tenant** — chave sem `tenant_id` vaza dado entre clientes.
- **Nunca inventar resultado de benchmark**; número sem comando é `NOT_TESTED`.

## Veredito
```
OTIMIZAÇÃO — <data>
ALVO:          <rota/serviço>
BASELINE:      p50=<X> p95=<Y> p99=<Z> (n=<volume>)
DEPOIS:        p50=<X'> p95=<Y'> p99=<Z'> (n=<volume>)
GANHO:         <Δ%> em <percentil>
BUDGET:        <declarado> → <cumprido/estourado>
NÃO OTIMIZADO: <lista>
PRÓXIMO:       <o que priorizar depois>
```

## Checklist de encerramento
- [ ] Baseline medido com volume
- [ ] Budget declarado antes da mudança
- [ ] Uma camada por vez
- [ ] Uma mudança por vez no diff
- [ ] Evidência before/after com o mesmo workload
- [ ] Regressão verificada (não ficou pior em outra camada)
- [ ] ADR criado se houve trade-off
- [ ] `benchmark-comparison.md` preenchido
- [ ] O que **não** foi otimizado está declarado
- [ ] Percentil e volume em toda afirmação

## Quality gates
Leia `references/quality-gates.md`. Resumo — BLOCKER: otimização sem baseline, ganho declarado sem medição comparável, budget ausente, regressão de correção/segurança, N+1 "corrigido" sem `EXPLAIN` antes/depois. MAJOR: mudança fora da camada do gargalo, índice criado sem `EXPLAIN`, cache sem invalidação declarada, virtualização sem teste de scroll, timeout ausente em dependência externa, sem RUM em produção.

## Seleção de referências (carregamento progressivo)
- Medição, baseline e instrumentos: `references/measurement-first.md`
- Budget e metas por camada: `references/perf-budget.md`
- Camada 1 — Frontend e interface: `references/frontend-layer.md`
- Camada 2 — Comunicação e rede: `references/network-layer.md`
- Camada 3 — Backend e banco: `references/backend-layer.md`
- Camada 4 — Infraestrutura e deploy: `references/infra-layer.md`
- Anti-padrões com correção: `references/anti-patterns.md`
- Gates e severidade: `references/quality-gates.md`
- Instalação: `references/installation.md`
- Templates: `templates/perf-plan.md`, `templates/layer-checklist.md`, `templates/perf-budget.md`, `templates/benchmark-report.md`
- Scripts: `scripts/web_vitals_probe.py` (sonda HTTP read-only), `scripts/compare_samples.py` (percentis antes/depois), `scripts/check_budget.py` (budget × benchmark), `scripts/validate_skill.py`

## Roteamento com outras skills
| Situação | Skill |
|---|---|
| Query, schema, índice, contrato de API | `dz23-backend-data-architect` |
| Interface, renderização, design system | `dz23-ultimate-pro-max` |
| Deploy, CDN, infra, rollback | `dz23-devops-cloud-deployer` |
| Prova E2E do fluxo após otimizar | `dz23-e2e-browser-verifier` |
| Mapear o código antes de mexer | `dz23-codebase-cartographer` |
| Especificar a otimização como requisito | `dz23-spec-to-system-engine` |
| Ciclo autônomo de correção | `dz23-autonomous-improvement-ultimate` |

Regra: **não crie um segundo orquestrador**. Esta skill decide onde cortar e prova o ganho; a execução é da skill do domínio.

## Contrato de resposta
Para tarefa executável: baseline medido (com comando/instrumento), gargalo localizado por camada, budget alvo, plano ordenado por impacto ÷ esforço com os itens das 4 camadas, custo de cada mudança, verificação antes/depois e o que **não** foi medido. Sem acesso ao sistema, entregue o plano de medição — nunca invente número.

## Gatilho de ativação
"Use a skill dz23-performance-scalability-engine, leia SKILL.md e as referências pertinentes, meça o baseline com instrumento real, localize o gargalo na camada certa, escreva o budget, corte com a menor mudança de maior impacto e me entregue o antes/depois. Não aceite otimização sem número, média no lugar de percentil nem 'ficou mais rápido' sem prova."
