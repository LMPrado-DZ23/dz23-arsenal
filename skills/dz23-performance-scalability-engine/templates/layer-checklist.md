# LAYER CHECKLIST — <produto> — <data>

> Estado: `APLICADO` · `N/A` (com motivo) · `PENDENTE` (com risco) · `BLOQUEADO`
> Nenhum item vira APLICADO sem evidência (comando, medição ou diff).

## Camada 1 — Frontend & Interface
| # | Item | Estado | Evidência | Diretriz |
|---|---|---|---|---|
| 1.1 | Skeleton loaders | | | mesma caixa do conteúdo; `aria-busy` |
| 1.2 | Mídia WebP/AVIF + lazy | | | `srcset`/`sizes`; sem lazy no LCP |
| 1.3 | Code splitting e terceiros | | | budget ≤170 KB; `async`/`defer` |
| 1.4 | Virtualização de listas | | | >100 linhas; testar scroll/foco |
| 1.5 | Debounce/throttle em input | | | 250–400 ms + `AbortController` |
| 1.6 | Fontes locais + cache | | | 2–3 pesos/variável + `immutable` |
| 1.7 | Resiliência mobile | | | 3G + CPU 4×; timeout curto |

## Camada 2 — Comunicação & Rede
| # | Item | Estado | Evidência | Diretriz |
|---|---|---|---|---|
| 2.1 | Sem duplicidade / `Promise.all` | | | `staleTime`; paralelo só independente |
| 2.2 | Streaming + UI otimista | | | SSE/chunked; proxy sem buffer |
| 2.3 | Timeout e resiliência | | | timeout menor que o do chamador; jitter |
| 2.4 | Paginação/cursor | | | keyset; cap no servidor |

## Camada 3 — Backend & Banco
| # | Item | Estado | Evidência | Diretriz |
|---|---|---|---|---|
| 3.1 | N+1 | | | queries não crescem com linhas |
| 3.2 | Índice composto | | | `CONCURRENTLY` + `EXPLAIN` antes/depois |
| 3.3 | Cache Redis | | | TTL + invalidação declarados |
| 3.4 | Fila para trabalho pesado | | | `202` + DLQ + idempotência |

## Camada 4 — Infraestrutura & Deploy
| # | Item | Estado | Evidência | Diretriz |
|---|---|---|---|---|
| 4.1 | CDN para estáticos | | | HTML `no-cache`; asset `immutable` |
| 4.2 | Brotli/GZIP | | | `Vary: Accept-Encoding`; não comprimir mídia |
| 4.3 | Proximidade app↔banco | | | mesma região; reduzir round-trips |
| 4.4 | Balanceamento de carga | | | `least_conn`; `/readyz` real |
| 4.5 | OTel + RUM | | | span por query; `release` no span |

## Resumo
- APLICADO: __ / 20
- N/A (motivado): __
- PENDENTE: __ (risco)
- BLOQUEADO: __

## Itens N/A declarados
| Item | Motivo |
|---|---|
