# Quality gates — evidência, não promessa

| Gate | PASS quando | Evidência mínima |
|---|---|---|
| Modelo de dados | Entidades, invariantes e chaves documentadas; constraints no banco | ERD/lista + DDL revisado |
| Contrato | OpenAPI/AsyncAPI atualizado; request/response/erro documentados | schema + teste de contrato |
| Autorização | Permissão por recurso; isolamento de tenant testado | teste de IDOR e de vazamento |
| Migração | Reversível; tempo e lock medidos; backfill idempotente | script up/down + medição |
| Integridade | Transação no escopo correto; idempotência em efeito colateral | teste de repetição/concorrência |
| Desempenho | Plano de execução medido; N+1 ausente; p95 da rota crítica | `EXPLAIN` antes/depois + medição |
| Observabilidade | Log estruturado com correlação; métricas e alerta do caminho novo | exemplo de log + painel/alerta |
| Segurança | Consulta parametrizada; segredo fora de código/log; PII fora de log | revisão + busca no diff |
| Resiliência | Timeout/retry/limite em toda dependência externa | código + teste de falha |
| Qualidade de código | Lint/typecheck/build/testes do projeto aprovados | logs dos comandos |
| Testes | Unit de regra + integração com banco real + contrato | saída da suíte, sem `skip` escondido |
| Documentação | README/ADR/runbook atualizados quando o comportamento muda | diff dos docs |

**Estados:** `PASS` (verificado), `PARTIAL`, `FAIL`, `NOT_TESTED`, `BLOCKED_BY_EXTERNAL_DEPENDENCY`. Não converta `NOT_TESTED` em `PASS`. Teste que não roda não conta.

## Severidade — o que reprova a entrega

**BLOCKER (não entrega, corrige antes):**
- Consulta com concatenação de entrada do usuário (injeção de SQL/comando).
- Rota que serve recurso de outro tenant ou de outro usuário sem checagem (IDOR / vazamento multi-tenant).
- Migração que reescreve tabela grande sem plano, ou `DROP`/`TRUNCATE` sem backup verificado.
- Dinheiro em ponto flutuante.
- Operação com efeito colateral (pagamento, e-mail, criação) sem idempotência.
- Segredo, token ou PII em código, log, mensagem de erro ou repositório.
- Endpoint que retorna dado fictício ou `mock` em caminho de produção.
- `NOT NULL`/constraint removida para "fazer passar".

**MAJOR (entrega só com ressalva registrada):**
- N+1 em rota de listagem.
- Paginação por offset em tabela grande sem limite máximo.
- Breaking change em contrato público sem deprecação.
- Índice criado sem query que o justifique, ou ausência de índice na consulta crítica.
- Transação aberta durante chamada de rede.
- Erro `500` para validação de entrada; mensagem que vaza detalhe interno.
- Timeout ausente em dependência externa.
- Teste de integração substituído por mock do próprio banco.

**MINOR (refinamento, registra e segue):**
- Nomenclatura inconsistente com o restante do schema.
- Log com campo redundante ou nível inadequado.
- Falta de índice parcial onde o volume ainda não dói.
- `SELECT *` em tabela pequena.

## Matriz de teste por componente
- **Endpoint**: sucesso, payload inválido, não autenticado, sem permissão, recurso de outro tenant, id inexistente, conflito de estado, rate limit.
- **Query**: plano de execução, volume realista, paginação no limite, ordenação estável.
- **Migração**: `up` → `down` → `up`; a partir de snapshot anonimizado; tempo e lock.
- **Transação/concorrência**: duas requisições simultâneas no mesmo recurso (dupla escrita, saldo, estoque).
- **Idempotência**: mesma chave duas vezes (mesmo payload e payload diferente).
- **Fila/job**: reprocessamento, DLQ, evento duplicado, job concorrente.
- **Integração externa**: timeout, erro 5xx, resposta lenta, resposta malformada.
- **Cache**: hit, miss, invalidação, chave por tenant.
- **Contrato**: schema contra payload real, campo novo opcional, campo removido detectado.

## Checklist final
- [ ] Modelo e invariantes documentados; constraints no banco.
- [ ] Contrato documentado e teste de contrato verde.
- [ ] Autorização por recurso e isolamento de tenant testados.
- [ ] Migração reversível, com lock e tempo medidos.
- [ ] Backfill idempotente e retomável (quando houver).
- [ ] Consulta parametrizada; nenhuma entrada concatenada.
- [ ] Plano de execução das queries alteradas medido antes/depois.
- [ ] N+1 verificado no log de query.
- [ ] Idempotência testada em operação com efeito colateral.
- [ ] Timeout/retry/limite em toda dependência externa.
- [ ] Log estruturado com correlação e sem PII.
- [ ] Suíte do projeto executada e comparada ao baseline.
- [ ] Rollback descrito e, quando possível, ensaiado.
- [ ] Riscos, pendências e o que não foi testado declarados.
