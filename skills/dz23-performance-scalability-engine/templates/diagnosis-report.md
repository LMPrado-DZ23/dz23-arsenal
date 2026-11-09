# Diagnosis Report — <projeto> — <data>

## Alvo
- Rota/handler/serviço: `<...>`
- Volume de referência: <N req/s> · <N usuários>
- Janela de coleta: <7d RUM | N req load test>
- Ambiente: <local | staging | prod> · build: `<sha>`

## Baseline
| Camada | Métrica | Valor atual | Budget | Gap |
|---|---|---|---|---|
| Frontend | LCP (p75) | | < 2,5 s | |
| Frontend | INP (p75) | | < 200 ms | |
| Frontend | CLS (p75) | | < 0,1 | |
| Rede | p95 API | | < 500 ms | |
| Rede | chamadas duplicadas | | 0 | |
| Backend | p99 DB | | < 2 s | |
| Backend | queries por request | | ≤ 3 | |
| Backend | N+1 em `GET <rota>` | sim/não | não | |
| Infra | cache hit ratio | | > 80% | |
| Infra | `Content-Encoding` | | br | |

## Gargalo identificado
- **Camada**: <Frontend | Rede | Backend | Infra>
- **Evidência**: `<EXPLAIN | waterfall | trace-id | Lighthouse>`
- **Hipótese**: <o que explica o tempo>
- **Hipóteses eliminadas**: <quais e como foram descartadas>

## O que NÃO foi medido
- <métrica/rota> — motivo: <sem instrumento | sem acesso | fora de escopo>

## Próximo passo
- Item da spec a atacar: <1.x | 2.x | 3.x | 4.x>
- Ver `optimization-plan.md`
