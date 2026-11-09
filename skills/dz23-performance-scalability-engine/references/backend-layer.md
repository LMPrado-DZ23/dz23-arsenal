<!--
  A spec original do usuário dizia "Filas para Processamento
  Assalariado" (typo em 3.4). Interpretado como "processamento
  assíncrono em filas/workers" (não RH). Original preservado em
  _sources/user-spec.md.
-->

# Camada 3 — Backend & Banco de dados (arquitetura)

Cada item: **problema que evita** · **como implementar** · **diretriz**.

## 3.1 Prevenção de N+1
**Evita** 1 query para a lista + N queries para as relações: 200 registros = 201 idas ao banco, cada uma com round-trip. É a causa nº 1 de endpoint lento em ORM.
**Implementar** detectar primeiro (log de query com contagem, `EXPLAIN` de padrão repetido, span por query no OTel); corrigir com `include`/`select_related`/`preload`/`join` em uma consulta, ou loader em lote (DataLoader) quando o ORM não resolve; proibir lazy load em serialização (o serializer tocando a relação é o gatilho clássico).
```ts
// ❌ N+1: 1 + N
const orders = await prisma.order.findMany();
for (const o of orders) o.customer = await prisma.customer.findUnique({ where: { id: o.customerId } });

// ✅ 2 queries fixas
const orders = await prisma.order.findMany({ include: { customer: true, items: true } });
```
```python
# ❌
for o in session.query(Order): print(o.customer.name)
# ✅
session.query(Order).options(selectinload(Order.customer), selectinload(Order.items))
```
**Diretriz** aceite: número de queries **não cresce** com o número de linhas. Prove com contador de query no teste (ex.: `assert query_count == 2`).

## 3.2 Indexação estratégica
**Evita** full scan em tabela grande; evita também o excesso de índice que mata escrita e ocupa disco.
**Implementar** listar as consultas mais frequentes (pg_stat_statements / slow query log), desenhar índice **composto na ordem do predicado** (igualdade → igualdade → range → ordenação), índice parcial para filtro seletivo, e cobrir quando o `SELECT` só usa colunas do índice.
```sql
-- consulta real: WHERE tenant_id = $1 AND status = $2 ORDER BY created_at DESC LIMIT 50
CREATE INDEX CONCURRENTLY idx_orders_tenant_status_created
  ON orders (tenant_id, status, created_at DESC, id DESC);

-- filtro seletivo recorrente
CREATE INDEX CONCURRENTLY idx_orders_pending
  ON orders (tenant_id, created_at DESC) WHERE status = 'pending';
```
**Diretriz** `CREATE INDEX CONCURRENTLY` em tabela viva (não trava escrita). Prova obrigatória: `EXPLAIN (ANALYZE, BUFFERS)` antes/depois — seq scan → index scan, e `rows`/`loops` coerentes. Índice sem `EXPLAIN` é aposta.

## 3.3 Camada de cache (Redis)
**Evita** recomputar/consultar o que muda pouco; evita latência de agregação cara em toda requisição.
**Implementar** cache-aside com chave versionada e TTL explícito; invalidação por evento (write invalida chave) ou TTL curto quando tolerável; `stampede` protection (lock curto ou `SETNX` para recomputar); cache de query para agregado, cache de objeto para entidade.
```ts
const key = `orders:v2:${tenantId}:${status}`;
const hit = await redis.get(key);
if (hit) return JSON.parse(hit);
const data = await db.query(...);
await redis.set(key, JSON.stringify(data), 'EX', 60);           // TTL 60 s
// no write: await redis.del(`orders:v2:${tenantId}:*`)  → prefira chaves por versão
```
**Diretriz** toda entrada declara **TTL**, **estratégia de invalidação** e **o que acontece se cache estiver errado**. Cache sem invalidação é dado errado com latência boa. Versionar a chave (`v2`) permite invalidação em massa sem varrer.

## 3.4 Filas para processamento assíncrono
**Evita** request presa em trabalho lento (e-mail, PDF, importação, chamada de IA) e timeout do cliente; evita pico derrubando a API.
**Implementar** publicar job e responder rápido (`202 Accepted` + id de acompanhamento); worker separado com concorrência configurada, retry com backoff e DLQ; idempotência por `jobId`/`event_id`; monitorar profundidade da fila e idade do job mais antigo.
```ts
// produtor: responde em ~50 ms
const job = await queue.add('send-invoice', { orderId }, { attempts: 5, backoff: { type: 'exponential', delay: 2000 }, jobId: `invoice:${orderId}` });
return res.status(202).json({ jobId: job.id });

// consumidor
worker = new Worker('send-invoice', async (job) => { await render(job.data.orderId); }, { concurrency: 8 });
```
**Diretriz** fila exige idempotência e DLQ; sem isso, retry duplica efeito. Trabalho de background não bloqueia resposta HTTP — se bloqueia, ainda não é fila.

## Ordem de ataque nesta camada
1. N+1 (maior ganho por linha de código) → 2. índice nas consultas quentes → 3. mover trabalho pesado para fila → 4. cache do que sobrou.

## Verificação
`EXPLAIN (ANALYZE, BUFFERS)` antes/depois; contador de queries por request; tempo de fila (p95 da idade) e profundidade; hit ratio do Redis. Sem esses quatro números, a camada não está medida.
