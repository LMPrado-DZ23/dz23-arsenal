# PERF PLAN — <produto/serviço> — <data>

> baseline: `<arquivo/medição>` · ambiente: <local|staging|prod> · janela: <n min>
> budget: `PERF-BUDGET.md` · gargalo localizado em: **camada <1|2|3|4>**

## 1. Diagnóstico
| Métrica | Baseline (p95) | Budget | Gap |
|---|---|---|---|
| LCP p75 | | ≤ 2,5 s | |
| INP p75 | | ≤ 200 ms | |
| p95 da rota crítica | | ≤ 300 ms | |
| queries por request | | ≤ 3 | |
| bundle inicial (gzip) | | ≤ 170 KB | |

**Onde o tempo vai** (trace/waterfall/EXPLAIN):
```
<ex.: 62% em q: orders.list (N+1, 41 queries) · 24% em bundle · 14% render>
```
**Evidência**: <comando/saída/trace-id>

## 2. Plano cirúrgico por camada
### Camada 1 — Frontend & Interface
| # | Item | Aplica? | Problema que evita | Como implementar | Ganho esperado | Esforço |
|---|---|---|---|---|---|---|
| 1.1 | Skeleton loaders | | layout shift/percepção | | | |
| 1.2 | Mídia WebP/AVIF + lazy | | payload e LCP | | | |
| 1.3 | Code splitting e terceiros | | TTI/INP | | | |
| 1.4 | Virtualização de listas | | DOM estourado | | | |
| 1.5 | Debounce/throttle em input | | request por tecla | | | |
| 1.6 | Fontes locais + cache | | FOIT/CLS e terceiro | | | |
| 1.7 | Resiliência mobile | | travamento em 3G | | | |

### Camada 2 — Comunicação & Rede
| # | Item | Aplica? | Problema que evita | Como implementar | Ganho esperado | Esforço |
|---|---|---|---|---|---|---|
| 2.1 | Sem chamada duplicada / `Promise.all` | | multiplicação de carga | | | |
| 2.2 | Streaming + UI otimista | | espera de LLM | | | |
| 2.3 | Timeout e resiliência | | thread presa, cascata | | | |
| 2.4 | Paginação/cursor | | payload e degradação | | | |

### Camada 3 — Backend & Banco
| # | Item | Aplica? | Problema que evita | Como implementar | Ganho esperado | Esforço |
|---|---|---|---|---|---|---|
| 3.1 | N+1 | | 1 + N queries | | | |
| 3.2 | Índice composto | | full scan | | | |
| 3.3 | Cache Redis | | recomputar caro | | | |
| 3.4 | Fila para trabalho pesado | | timeout na request | | | |

### Camada 4 — Infraestrutura & Deploy
| # | Item | Aplica? | Problema que evita | Como implementar | Ganho esperado | Esforço |
|---|---|---|---|---|---|---|
| 4.1 | CDN para estáticos | | RTT distante | | | |
| 4.2 | Brotli/GZIP | | bytes desnecessários | | | |
| 4.3 | Proximidade app↔banco | | RTT por query | | | |
| 4.4 | Balanceamento de carga | | teto de instância única | | | |
| 4.5 | OTel + RUM | | descobrir pelo cliente | | | |

## 3. Ordem de execução (impacto ÷ esforço)
| # | Mudança | Camada | Ganho estimado | Custo | Dono |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |

## 4. Verificação
| Mudança | Instrumento | Antes | Depois | Δ |
|---|---|---|---|---|
| | | | | |

## 5. Guarda de regressão
- [ ] Budget no CI (`<comando>`)
- [ ] Alerta de SLO (p95 > budget por 10 min)
- [ ] Painel RUM publicado em `<url>`

## 6. O que NÃO foi medido
- <métrica/rota> — motivo: <sem instrumento | sem acesso | fora de escopo>
