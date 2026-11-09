# Anti-padrões de performance

Cada item: **sintoma** → **por que dói** → **correção**.

## Processo
1. **Otimizar sem baseline** → não se sabe se melhorou → medir antes, com instrumento e ambiente declarados.
2. **Média no lugar de percentil** → cauda invisível → p50/p95/p99 (p75 para vitals).
3. **Várias mudanças de uma vez** → nenhuma conclusão causal → uma mudança, uma medição.
4. **Micro-otimizar o irrelevante** → 2 ms no parser enquanto a query leva 800 ms → perfil primeiro.
5. **"Ficou mais rápido" sem número** → fé, não engenharia → antes/depois com o mesmo instrumento.
6. **Comparar build de dev com produção** → ganho fictício → mesmo build, mesmo dado, mesmo ambiente.
7. **Medir com cache aquecido e chamar de real** → esconde o pior caso → medir frio e quente e dizer qual é qual.

## Camada 1 — Frontend
8. **Skeleton que muda de tamanho** → vira CLS → dimensão reservada igual ao conteúdo.
9. **`loading="lazy"` na imagem de LCP** → atrasa o maior elemento → `fetchpriority="high"` e sem lazy.
10. **`sizes` errado no `srcset`** → baixa o arquivo maior → `sizes` real por breakpoint.
11. **JPEG/PNG de 2 MB** → LCP alto → AVIF/WebP + `srcset`.
12. **JS de terceiro síncrono no `<head>`** → bloqueia render → `defer`/`async` ou após interação.
13. **Biblioteca de chart no bundle inicial** → +300 KB → `dynamic()` com `ssr:false`.
14. **Lista com 5.000 nós no DOM** → scroll travado → virtualização.
15. **Virtualizar sem testar teclado/`Ctrl+F`** → acessibilidade quebrada → teste E2E de scroll e foco.
16. **Busca sem debounce** → request por tecla → debounce 250–400 ms.
17. **Debounce sem cancelamento** → resultado fora de ordem → `AbortController`.
18. **4 pesos de fonte do Google Fonts** → requisição a terceiro no crítico → self-host + variável + `swap`.
19. **`Cache-Control` sem hash no nome** → asset preso → hash + `immutable`.
20. **"Funciona no desktop"** → mobile quebra → throttle 3G + CPU 4×.

## Camada 2 — Rede
21. **Mesma query disparada por 5 componentes** → 5× carga → fonte única de verdade + `staleTime`.
22. **`Promise.all` com dependência** → impossível, ou pior: falha em cascata → paralelo só entre independentes.
23. **`await` em sequência no que era paralelo** → soma dos tempos → `Promise.all`.
24. **Esperar LLM inteiro** → 20 s de tela parada → streaming + append incremental.
25. **Streaming com proxy bufferizando** → chega tudo no fim → desligar buffer / `X-Accel-Buffering: no`.
26. **Sem timeout em API externa** → thread presa, fila cresce → timeout por camada, menor que o do chamador.
27. **Retry sem jitter** → tempestade sincronizada → backoff exponencial com jitter e teto.
28. **Retry em operação não idempotente** → duplicidade → `Idempotency-Key` / `jobId`.
29. **`OFFSET 50000`** → varre e descarta → keyset/cursor.
30. **Listagem sem teto** → `?limit=100000` derruba o banco → cap no servidor.

## Camada 3 — Backend
31. **N+1 no serializer** → 1 + N queries → `include`/`selectinload`/batch loader.
32. **"Corrigi o N+1" sem contador de query** → pode ser 1 + N/2 → teste que conta queries.
33. **Índice sem `EXPLAIN`** → pode não ser usado → plano antes/depois.
34. **Índice em coluna de baixa cardinalidade isolada** → o planner ignora → composto com a coluna seletiva primeiro.
35. **`CREATE INDEX` sem `CONCURRENTLY`** → trava escrita → concorrente em produção.
36. **Índice para tudo** → escrita lenta e disco cheio → índice nas consultas quentes, medido.
37. **Cache sem invalidação** → dado errado e rápido → TTL + invalidação por evento declarados.
38. **Cache sem TTL** → dado eterno → TTL explícito.
39. **Cache stampede** → todas as réplicas recomputam juntas → lock curto/`SETNX`.
40. **Trabalho pesado na request** → timeout e 502 → fila + `202` + DLQ + idempotência.

## Camada 4 — Infra
41. **HTML com `immutable`** → usuário preso na versão antiga → `no-cache`/`s-maxage` curto no HTML.
42. **Sem Brotli/GZIP** → 3–5× mais bytes → compressão na borda/proxy + `Vary`.
43. **Comprimir imagem** → CPU à toa → só texto/JS/CSS/JSON/SVG.
44. **App longe do banco** → 80 ms × N queries → co-localizar; reduzir round-trips.
45. **Autoscaling por CPU em workload I/O-bound** → escala tarde → latência p95 / profundidade de fila.
46. **Health check que não checa dependência** → instância quebrada no pool → `/readyz` real.
47. **Sem OTel/RUM** → descobre pelo cliente → span por query + `web-vitals`.
48. **Alerta sem SLO** → ruído → alerta no budget, por 10 min.
49. **Otimizar sem `release` no trace** → não sabe qual deploy degradou → `release`/`git_sha` no span.

## Como usar
Percorra na revisão: **não se aplica / aplicado / pendente com risco**. Achado BLOCKER (ver `quality-gates.md`) bloqueia a entrega do plano.
