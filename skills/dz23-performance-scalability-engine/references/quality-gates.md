# Quality gates — prova ou não aconteceu

| Gate | PASS quando | Evidência mínima |
|---|---|---|
| Baseline | medido com instrumento, ambiente e janela | tabela + comando |
| Percentil | p50/p95/p99 (p75 em vitals) | números por rota/endpoint |
| Gargalo | localizado em **uma** camada | trace, `EXPLAIN`, waterfall ou perfil |
| Budget | alvo declarado antes da mudança | `perf-budget.md` |
| Mudança | mínima, na camada do gargalo | diff pequeno e justificado |
| Prova | antes/depois com o mesmo instrumento | tabela comparativa |
| Regressão | sem piora em métrica não-alvo | comparativo completo |
| Guarda | budget no CI ou alerta de SLO | pipeline/alerta |
| Custo | memória/CPU/dinheiro declarados | estimativa por mudança |

**Estados:** `PASS`, `PARTIAL`, `FAIL`, `NOT_TESTED`, `BLOCKED_BY_EXTERNAL_DEPENDENCY` (sem acesso a produção, banco ou carga).

## Severidade

**BLOCKER:**
- Otimização sem baseline numérico.
- Ganho declarado sem medição comparável (ambiente/dado/build diferentes).
- Budget ausente.
- Regressão de correção ou segurança em troca de latência.
- N+1 "corrigido" sem contador de query ou `EXPLAIN`.
- Cache introduzido sem estratégia de invalidação declarada.

**MAJOR:**
- Mudança fora da camada do gargalo.
- Índice criado sem `EXPLAIN` antes/depois.
- Virtualização ou code splitting sem teste no fluxo real.
- Timeout ausente em dependência externa tocada.
- Sem RUM/OTel no caminho otimizado.
- Custo da mudança não declarado.

**MINOR:**
- Skeleton com dimensão aproximada.
- Nome de métrica sem unidade.
- Falta de nota sobre o ambiente de medição.

## Checklist final
- [ ] Baseline por rota/endpoint com instrumento e janela.
- [ ] Percentis (p50/p95/p99; p75 em vitals).
- [ ] Gargalo localizado em uma camada, com evidência.
- [ ] Budget alvo escrito antes da mudança.
- [ ] Itens das 4 camadas revisados: aplicável / aplicado / não se aplica.
- [ ] Mudança mínima com diff explicado.
- [ ] Antes/depois com o mesmo instrumento (carga, dado, build).
- [ ] Nenhuma regressão em métrica não-alvo.
- [ ] Custo (memória, CPU, dinheiro, complexidade) declarado.
- [ ] Guarda de regressão instalada (CI ou alerta).
- [ ] O que **não** foi medido está declarado.
