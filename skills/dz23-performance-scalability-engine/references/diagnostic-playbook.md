# Playbook de diagnóstico

## Regra
Não otimize antes de saber **em qual camada** está o tempo. A maioria das otimizações erradas nasce de "achismo": o sintoma é na tela, então se otimiza o frontend — quando o gargalo é uma query de 800 ms.

## Sintoma → camada provável → primeira medição
| Sintoma | Camada provável | Primeira medição |
|---|---|---|
| LCP > 4 s | frontend | Lighthouse (mobile throttled) + waterfall do elemento |
| CLS > 0.25 | frontend | Lighthouse + identificar elemento que desloca |
| INP > 500 ms | frontend (main thread) | Performance panel: long tasks, re-render |
| Tela branca por segundos | rede ou render | DevTools Network: TTFB vs primeiro pixel |
| API lenta | backend | APM/trace por span + `EXPLAIN (ANALYZE, BUFFERS)` |
| Lista travando | frontend (DOM) | contagem de nós (`document.querySelectorAll('*')`) |
| 502 / 504 | infra | log do load balancer + timeout do upstream |
| Timeout esporádico | rede/infra | distribuição de latência p99 + connection pool |
| "Lento para alguns usuários" | infra (geo) | latência por região; distância app↔banco |
| Custo de infra alto | backend/infra | CPU por request, cache hit ratio, N+1 |

## Bisecção (isolar a camada em 4 medições)
1. **Medir o servidor isolado**: `curl -w` no endpoint (sem browser, sem CDN) → separa rede de servidor.
2. **Medir sem cache**: desligue Redis/CDN e meça. Se piorar muito, o cache estava fazendo trabalho pesado (ou mascarando problema).
3. **Medir sem CDN**: request direto na origem → mede a distância e a borda.
4. **Medir só o handler**: profile/flamegraph sem serialização → separa lógica de I/O.
5. **Medir só a query**: `EXPLAIN (ANALYZE, BUFFERS)` com o mesmo plano de acesso e volume real.

Cada passo elimina uma hipótese. Sem eliminar hipótese, você está otimizando por intuição.

## Árvore de decisão rápida
```
O tempo está no cliente ou no servidor?
├─ cliente (waterfall mostra render/bundle)
│   ├─ bundle grande        → 1.3 code splitting
│   ├─ imagem de LCP pesada → 1.2 mídia
│   ├─ CLS                  → 1.1 skeleton com dimensão
│   ├─ INP alto             → 1.4 virtualização / 1.5 debounce
│   └─ fonte bloqueando     → 1.6 self-host + preload
└─ servidor (TTFB alto)
    ├─ p95 alto e CPU alta  → query/lógica: 3.1 N+1, 3.2 índice
    ├─ p95 alto e CPU baixa → I/O/espera: 2.3 timeout, 4.3 proximidade
    ├─ picos                → 3.4 fila, 3.3 cache
    └─ erro/timeout         → 4.4 balanceamento, connection pool
```

## Ferramentas por camada (quando disponíveis)
| Camada | Ferramenta | Uso |
|---|---|---|
| Frontend | Lighthouse CI, `web-vitals`, bundle analyzer | LCP/CLS/INP, peso de chunk |
| Rede | DevTools/Playwright waterfall, `curl -w` | duplicidade, TTFB, streaming |
| Backend | OTel/APM, `pg_stat_statements`, `EXPLAIN` | queries/request, plano de execução |
| Infra | CDN analytics, `curl -H 'Accept-Encoding: br'`, RUM | hit ratio, compressão, latência por região |

Quando a ferramenta não existe, o estado é `BLOCKED_BY_EXTERNAL_DEPENDENCY` — **não** se estima o número.

## Hotspots de código
Antes de medir tudo, use `dz23-codebase-cartographer` para localizar as áreas com mais churn e complexidade. Otimizar código que ninguém toca e ninguém usa é desperdício, mesmo que seja feio.

## Sinais de que a medição está errada
- Resultado muda > 30% entre execuções idênticas → ambiente ruidoso; isole.
- p95 ≈ p50 em carga alta → amostra pequena ou cache aquecido.
- Depois "melhorou" em tudo ao mesmo tempo → provavelmente mediu outro ambiente.
- Número não reproduz no CI → instrumento diferente ou dado diferente.

## Saída
Camada do gargalo com evidência (trace/EXPLAIN/waterfall), a medição que eliminou as outras hipóteses, e a primeira ação a executar.
