# Budget de performance

## O que é
Budget é o teto acordado, medido no percentil combinado, que **bloqueia merge** quando estourado. Sem budget, "melhorou" não tem significado e "piorou" passa despercebido.

## Budgets de referência
| Métrica | Bom | Aceitável | Ruim |
|---|---|---|---|
| LCP (p75) | < 2,0 s | 2,0–2,5 s | > 2,5 s |
| INP (p75) | < 150 ms | 150–200 ms | > 200 ms |
| CLS (p75) | < 0,05 | 0,05–0,1 | > 0,1 |
| TTFB (p75) | < 500 ms | 500–800 ms | > 800 ms |
| JS inicial (gzip) | < 130 KB | 130–170 KB | > 170 KB |
| CSS inicial (gzip) | < 30 KB | 30–50 KB | > 50 KB |
| Imagem de LCP | < 150 KB | 150–300 KB | > 300 KB |
| API read (p95) | < 200 ms | 200–400 ms | > 400 ms |
| API write (p95) | < 400 ms | 400–800 ms | > 800 ms |
| Query simples (p95) | < 10 ms | 10–50 ms | > 50 ms |
| Query agregada (p95) | < 100 ms | 100–300 ms | > 300 ms |
| Taxa de erro | < 0,1% | 0,1–1% | > 1% |

Ajuste ao produto: app de trading e dashboard interno não têm o mesmo budget de um blog.

## Como escrever o budget
```
BUDGET — <produto> — <data>
Rota/endpoint            métrica      alvo      medido    estado
/                        LCP p75      ≤ 2,5 s   3,8 s     FAIL
/api/orders (GET)        p95          ≤ 300 ms  920 ms    FAIL
/api/orders (POST)       p95          ≤ 500 ms  310 ms    PASS
q: orders.list           p95          ≤ 50 ms   380 ms    FAIL
bundle inicial           gzip         ≤ 170 KB  412 KB    FAIL
```
Cada linha tem instrumento, ambiente e janela (ver `measurement-first.md`).

## Budget de recurso e custo
Performance sem custo declarado vira conta alta. Registre por mudança:
- memória adicional do cache (entradas × tamanho médio);
- CPU do índice novo (escrita mais lenta, disco);
- instância extra/CDN (R$/mês);
- complexidade (mais um serviço para operar).

## Priorização (impacto × esforço / ICE)
**Impacto** = usuários afetados × % de ganho esperado × criticidade da rota.
**Esforço** = dias-pessoa + risco de regressão.
**Critério de desempate**: segurança e integridade de dados primeiro; depois rotas críticas de receita.

| # | Item (camada) | Impacto | Esforço | ICE | Ordem |
|---|---|---|---|---|---|
| 1 | N+1 em `GET /orders` (backend) | alto | baixo | 9 | 1 |
| 2 | Brotli + CDN de assets (infra) | alto | baixo | 9 | 2 |
| 3 | Code splitting da rota pesada (frontend) | médio | médio | 4 | 3 |
| 4 | Virtualizar tabela de 5.000 linhas (frontend) | médio | médio | 4 | 4 |
| 5 | Cache Redis de catálogo (backend) | médio | alto | 2 | 5 |

ICE = (Impacto × 2) + (3 − Esforço) em escala 1–3, apenas para ordenar — não é medida física.
Item com esforço alto e impacto baixo fica **fora** do ciclo atual, com motivo registrado.

## Priorização: impacto ÷ esforço
| Item | Impacto (ms ou KB) | Esforço | Nota |
|---|---|---|---|
| corrigir N+1 do pedido | −600 ms p95 | baixo | primeiro |
| índice composto | −250 ms | baixo | segundo |
| code splitting da rota pesada | −300 KB | médio | terceiro |
| virtualizar tabela | −200 ms INP | médio | quarto |
| CDN | −150 ms TTFB | baixo (config) | depende de infra |

Ordem = maior ganho por menor custo, **na camada que o baseline apontou**. Não comece pela camada mais fácil de editar.

## Regra dos 80/20 verificada
Meça a distribuição do tempo antes de escolher: no caminho quente, uma ou duas causas costumam responder por 70–90% do tempo. Se o gráfico não mostra concentração, a medição está errada (amostra pequena, ambiente ruidoso ou métrica errada).

## Quando o budget não fecha
1. Reduza escopo (menos dado por request, paginação menor).
2. Mude o desenho (assíncrono, pré-computado, cache).
3. Compre capacidade (scale up/out) — último recurso, com custo declarado.
4. Negocie o budget com o produto — **explicitamente**, nunca em silêncio.

## Saída
Tabela de budget com estado PASS/FAIL por linha, priorização por impacto ÷ esforço e o custo de cada mudança.
## Verificação automatizada do budget

O gate pode ser executado por script, sobre artefatos que você preencheu (ele **não** mede nada):

```bash
python scripts/check_budget.py --budget projects/<p>/perf/performance-budget.md \
                               --benchmark projects/<p>/perf/benchmark-comparison.md
```
- Exit `0` = todas as métricas dentro do budget (`BUDGET_PASS`) ou alguma sem medição (`BUDGET_PARTIAL`);
- Exit `1` = métrica acima do budget (`BUDGET_FAIL`);
- Exit `2` = input inválido.

Ele só parseia as tabelas markdown dos dois arquivos. A medição continua sendo sua: Lighthouse, k6,
`EXPLAIN`. Script que "mede" sem instrumento é script que mente.
