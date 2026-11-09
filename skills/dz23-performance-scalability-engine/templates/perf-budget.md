# PERF BUDGET — <produto> — <data>

> Instrumento: <Lighthouse CI | web-vitals RUM | k6 | EXPLAIN | APM>
> Ambiente: <local | staging | prod> · Dado: <volume real | sintético> · Janela: <n min>

## Web vitals (p75)
| Métrica | Budget | Medido | Estado |
|---|---|---|---|
| LCP | ≤ 2,5 s | | |
| INP | ≤ 200 ms | | |
| CLS | ≤ 0,1 | | |
| TTFB | ≤ 800 ms | | |

## Bundle
| Recurso | Budget (gzip) | Medido | Estado |
|---|---|---|---|
| JS inicial | ≤ 170 KB | | |
| CSS inicial | ≤ 50 KB | | |
| Imagem de LCP | ≤ 300 KB | | |
| Fonte acima da dobra | ≤ 60 KB | | |

## API (p95)
| Endpoint | Tipo | Budget | Medido | Estado |
|---|---|---|---|---|
| `GET /api/...` | read | ≤ 300 ms | | |
| `POST /api/...` | write | ≤ 500 ms | | |

## Banco
| Consulta | Budget (p95) | Medido | Queries/req | Estado |
|---|---|---|---|---|
| `q: ...` | ≤ 50 ms | | ≤ 3 | |

## Infra
| Item | Budget | Medido | Estado |
|---|---|---|---|
| Taxa de erro | ≤ 0,1% | | |
| p95 por instância | ≤ budget da rota | | |
| Profundidade de fila | ≤ 100 | | |
| Idade do job mais antigo | ≤ 60 s | | |
| Custo por 1k requests | ≤ R$ ___ | | |

## Regras
- Toda linha tem instrumento, ambiente e janela.
- `FAIL` bloqueia merge (ou exceção registrada com prazo e dono).
- Budget muda por decisão explícita, nunca por conveniência.

## Exceções
| Linha | Motivo | Aprovador | Prazo |
|---|---|---|---|
