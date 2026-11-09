# Desempenho e observabilidade

## Índice nasce da query
1. Capture a query real (log de slow query, `pg_stat_statements`, tracing).
2. `EXPLAIN (ANALYZE, BUFFERS)` antes — guarde o plano.
3. Proponha o índice com a coluna de igualdade primeiro, depois range, depois ordenação.
4. Meça depois, no mesmo volume. Sem medição, é opinião.

Regras: índice composto na ordem de uso (`WHERE tenant_id = ? AND status = ? ORDER BY created_at` → `(tenant_id, status, created_at)`); índice parcial para consulta seletiva (`WHERE deleted_at IS NULL`); cobrir a consulta (`INCLUDE`) evita heap fetch em leitura quente; índice não usado é custo de escrita — remova após medir.

## N+1 e acesso a dados
- N+1 é proibido: carregue por join, `IN` em lote ou DataLoader. Em ORM, verifique a query gerada (log), não a intenção.
- Evite `SELECT *`; traga só as colunas usadas.
- Contagem em lista: `count(*)` separado ou contador materializado, nunca `SELECT *` para contar.
- Lote: `INSERT ... VALUES (...)`, `COPY` para volume; `UPDATE ... FROM (VALUES ...)`.

## Cache
| Camada | Uso | Invalidação |
|---|---|---|
| HTTP (`Cache-Control`, ETag) | resposta pública/pouco mutável | versão/tag do recurso |
| Aplicação (Redis/memória) | leitura quente, cálculo caro | chave versionada + TTL + invalidação por evento |
| Banco (matview) | agregação pesada | refresh agendado/`CONCURRENTLY` |
Regras: toda chave de cache inclui o tenant; nunca cachear dado de autorização sem o escopo; TTL sempre; cache stampede evitado com lock/single-flight; invalidação declarada — se não sabe invalidar, não cacheie.

## Pool e conexões
Pool dimensionado por `(núcleos × 2) + réplicas` como ponto de partida, com fila e timeout de aquisição. Pool da aplicação × nº de instâncias precisa caber no `max_connections` do banco (use PgBouncer quando não couber). Conexão vazada derruba o serviço devagar — monitore `idle in transaction`.

## Meta e medição
- Latência por rota em **p50/p95/p99**, não média. Média esconde a cauda.
- SLO declarado por rota crítica (ex.: p95 < 300 ms) e orçamento de erro; alerta queima quando o SLO queima.
- Throughput e saturação (CPU, conexões, fila, lag de réplica) no mesmo painel.
- Carga: teste de fumaça com volume realista e cenário de pico; reporte antes/depois, não só depois.

## Observabilidade
- Log **estruturado** (JSON) com `timestamp`, `level`, `service`, `request_id`/`trace_id`, `route`, `status`, `duration_ms`, `tenant_id` (sem PII).
- Correlação ponta a ponta: `trace_id` propagado do cliente ao banco e à fila.
- Métricas: latência, taxa de erro, saturação, fila/DLQ, cache hit ratio, lag de replicação.
- Alerta com ação (o que fazer), não só "algo falhou". Todo alerta tem dono e runbook.
- Erro agrupado com stack no coletor, mensagem curta ao cliente com `request_id`.

## Consultas de diagnóstico
`pg_stat_activity` para lock/idle in transaction, `pg_stat_statements` para topo de custo, `pg_locks` para bloqueio, `EXPLAIN` para plano real, `pg_stat_user_indexes` para índice nunca usado, réplica com `pg_stat_replication` para lag.

## Critério de saída de performance
(a) plano antes/depois das queries alteradas; (b) N+1 verificado no log de query; (c) p95 medido da rota crítica; (d) índice justificado por consulta; (e) cache com invalidação declarada; (f) dashboard/alerta para o novo caminho.
