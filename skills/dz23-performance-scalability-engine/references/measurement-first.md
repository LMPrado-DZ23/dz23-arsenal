# Medição e baseline

## Regra
Sem baseline, não existe otimização — existe mudança de código com opinião anexada. A primeira entrega desta skill é **número**, não patch.

## O que medir, por camada
| Camada | Instrumento | Métrica |
|---|---|---|
| Frontend | `web-vitals` (RUM) + Lighthouse (lab) | p75 LCP, INP, CLS, TTFB; peso do bundle inicial |
| Rede | DevTools/Playwright waterfall, proxy log | nº de requests por rota, duplicidade, p95 por endpoint, TTFB |
| Backend | OTel span por query, `pg_stat_statements`, `EXPLAIN (ANALYZE, BUFFERS)` | queries por request, tempo de query p95, rows/loops |
| Infra | APM/OTel, painel do balanceador | p95 por instância, CPU/memória, profundidade de fila, custo |

## Percentil, sempre
Média esconde a cauda — e é a cauda que o usuário sente.
```
p50  ok | p95  é o que reclama no suporte | p99  é o que vira incidente
```
Reporte p50/p95/p99 por rota; para vitals, o padrão do mercado é **p75** (Core Web Vitals usa p75).

## Baseline mínimo por alvo
```
ALVO: <rota | endpoint | job>
AMBIENTE: <local | staging | prod> · dado: <volume real | sintético>
JANELA: <n minutos / n requisições>
p50 / p95 / p99:
throughput (req/s) no ponto de degradação:
recurso no limite (CPU/RAM/IO/conexões):
custo por 1k requisições:
```
Sem ambiente e volume declarados, o número não é comparável — e comparação inválida é pior que nenhuma.

## Sintético × RUM
| | Sintético (Lighthouse, k6) | RUM (web-vitals, OTel real) |
|---|---|---|
| Vantagem | reprodutível, roda no CI | mede o usuário real, device e rede reais |
| Limite | laboratório, não representa a cauda | ruidoso, precisa volume e amostragem |
| Uso | gate de regressão | diagnóstico e priorização |

Use os dois: sintético **guarda**, RUM **decide**.

## Localizar o gargalo (ordem)
1. **Onde o tempo vai**: trace/waterfall mostra se é rede, servidor, query ou render.
2. **Se é servidor**: CPU (perfil), memória (GC/leak), espera de I/O, lock.
3. **Se é query**: `EXPLAIN (ANALYZE, BUFFERS)` — `Seq Scan` grande, `rows` estimado ≠ real, `loops` alto (N+1).
4. **Se é cliente**: bundle inicial (analyzer), LCP element, long task (INP).
5. **Se é infra**: distância, compressão, conexão, instância saturada.

## Teste de carga honesto
```bash
k6 run --vus 50 --duration 2m script.js          # carga constante
k6 run --stage 30s:0,2m:50,2m:200,1m:0 script.js # rampa: acha o joelho
```
- Rampa encontra o ponto de degradação; carga constante prova estabilidade.
- Dado realista: 10 registros não exercita índice nem paginação.
- Aqueça o cache antes de medir (ou meça frio de propósito e diga qual).
- Meça o **cliente de destino** também: servidor rápido com payload de 5 MB continua lento para o usuário.

## Armadilhas de medição
- Medir com `console.log` e chamar de perfil.
- Comparar antes/depois em máquina diferente, dado diferente ou build de dev.
- Otimizar microbenchmark irrelevante (parser de 2 ms) e ignorar query de 800 ms.
- Rodar carga contra ambiente compartilhado e culpar o código.
- Confundir cache aquecido com performance real.

## Comparação de amostras (`compare_samples.py`)
Para comparar antes/depois sem planilha manual, use o helper da skill:
```bash
python scripts/compare_samples.py antes.json depois.json            # texto
python scripts/compare_samples.py antes.json depois.json --json      # JSON
python scripts/compare_samples.py antes.json depois.json --out cmp.json
```
- Entrada: dois JSON com `metadata` + `samples` (lista de latências em ms).
- Percentis por **nearest-rank** (`ceil(q*n)`) — p50, p75, p95, p99.
- Metadata (`workload`, `cohort`, `cache_state`, `sample_source`) precisa ser **idêntica** nos dois
  arquivos; se não for, **exit 3** — comparação inválida, não "quase igual".
- Saída declara sempre `DESCRIPTIVE_COMPARISON_ONLY`, `performance_pass=false`,
  `benchmark_executed=false` e `context_verified=false`: o script **descreve** números, não aprova
  performance e não executa benchmark.
- Exit: `0` comparação estruturalmente válida · `1` falha de cálculo · `2` input inválido · `3` bloqueada.

Regra: comparação válida exige mesmo workload, mesma coorte, mesmo estado de cache e mesma origem de
amostra. Qualquer divergência torna o ganho fictício — o script barra em vez de deixar passar.

## Saída
Tabela de baseline com instrumento, ambiente, janela e percentis; e a conclusão de **qual camada** concentra o tempo.
