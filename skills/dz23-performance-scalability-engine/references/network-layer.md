# Camada 2 — Comunicação & Rede (APIs e fluxos)

Cada item: **problema que evita** · **como implementar** · **diretriz**.

## 2.1 Prevenção de duplicidade
**Evita** mesma chamada disparada em mount, re-render, StrictMode (dev), múltiplos componentes e navegação — multiplicando carga e tornando a UI refém da chamada mais lenta.
**Implementar** uma fonte de verdade por dado (React Query/SWR dedupe por chave); `staleTime` explícito; chamada no nível do componente-pai ou no loader da rota, não em cada filho; `Promise.all` para requisições **independentes** e `Promise.allSettled` quando uma falha não deve derrubar as outras.
```ts
// dedupe por chave + cache curto: 5 componentes, 1 request
const { data } = useQuery({ queryKey: ['orders', id], queryFn: () => getOrder(id), staleTime: 30_000 });

// paralelo quando independentes
const [user, plans, invoices] = await Promise.all([getUser(id), getPlans(), getInvoices(id)]);
```
**Diretriz** `Promise.all` só entre chamadas independentes; em cascata (B depende de A) paralelizar é impossível — o ganho vem de mover a água (BFS: buscar em lotes) ou de cache. Duplicidade em dev por StrictMode é esperada; em produção não.

## 2.2 Streaming e otimização de IA
**Evita** espera de 10–30 s por resposta completa de LLM, UI congelada e timeout do proxy; evita re-render por token.
**Implementar** no servidor: SSE (`text/event-stream`) ou streaming HTTP com `Transfer-Encoding: chunked`; no cliente: `ReadableStream` + append incremental, sem re-renderizar a árvore inteira a cada token (estado isolado no componente do texto); desabilitar buffering no proxy (`proxy_buffering off` no Nginx).
```ts
// cliente: append incremental
const res = await fetch('/api/chat', { method: 'POST', body: JSON.stringify({ q }) });
const reader = res.body!.getReader(); const dec = new TextDecoder();
for (;;) { const { value, done } = await reader.read(); if (done) break;
  setText(prev => prev + dec.decode(value, { stream: true })); }
```
```python
# servidor (FastAPI/SSE mínimo)
async def stream(): yield f"data: {json.dumps({'delta': tok})}\n\n"
return StreamingResponse(stream(), media_type="text/event-stream",
                         headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
```
**Diretriz** streaming exige proxy sem buffer e cliente que não re-renderiza tudo. UI otimista é para ação de efeito conhecido (like, envio) — não para resultado que você não pode prever.

## 2.3 Timeouts e resiliência
**Evita** conexão pendurada consumindo worker/thread (o clássico "o servidor morreu, mas o processo está vivo"), cascata de lentidão e retry em tempestade.
**Implementar** timeout **menor** que o do chamador (regra: timeout do cliente > timeout do serviço > timeout da dependência); `AbortController` no browser e `httpx`/`fetch` com timeout no servidor; retry só em idempotente, com backoff exponencial + jitter e teto de tentativas; circuit breaker em dependência instável; deadline propagado (header `X-Request-Deadline`).
```ts
const ctrl = new AbortController(); const t = setTimeout(() => ctrl.abort(), 5000);
const r = await fetch(url, { signal: ctrl.signal, headers: { 'X-Request-Id': rid } }).finally(() => clearTimeout(t));
```
```python
httpx.Client(timeout=httpx.Timeout(connect=2.0, read=5.0, write=5.0, pool=1.0))
# retry com jitter, teto 3
for attempt in range(3):
    try: return do()
    except TransientError: sleep(min(2 ** attempt + random.random(), 8))
```
**Diretriz** timeout no topo sem timeout na dependência é teatro: a requisição "termina" e a chamada de baixo continua queimando recurso. Sempre limite por camada.

## 2.4 Paginação eficiente
**Evita** payload de dezenas de MB, memória do servidor e do cliente, e a página que fica mais lenta a cada mês.
**Implementar** cursor/keyset (`WHERE (created_at, id) < (?, ?) ORDER BY created_at DESC, id DESC LIMIT ?`) para listagem grande e ordenável; offset só em conjunto pequeno/estável; limite máximo no servidor (cap 100); campo `next_cursor` explícito e `total` opcional (contagem exata custa caro — use estimativa).
```sql
-- keyset: O(limite), não O(offset)
SELECT id, created_at FROM orders
 WHERE (created_at, id) < ($1, $2)
 ORDER BY created_at DESC, id DESC LIMIT 50;
```
**Diretriz** `OFFSET 50000` varre e descarta 50 mil linhas — é o vilão de listagem antiga. Keyset exige índice composto coerente com a ordenação (ver camada 3).

## Ordem de ataque nesta camada
1. duplicidade (custo zero, ganho imediato) → 2. timeout (evita incidente) → 3. paginação (evita degradação) → 4. streaming/otimista (UX percebida).

## Verificação
Waterfall do DevTools/Playwright (`request` events) para duplicidade; contagem de requests por rota; tempo até primeiro byte no streaming; teste de carga com a dependência lenta (chaos: latency 5 s) para provar o timeout.
