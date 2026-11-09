# Anti-padrões de backend, dados e contrato

Cada item: **sintoma** → **por que dói** → **correção**.

## Dados
1. **Dinheiro em `float`** → `0.1 + 0.2 ≠ 0.3` em ponto flutuante; arredondamento erra em soma, imposto e conciliação → inteiro em centavos ou `numeric`, com moeda explícita. Nunca compare float por igualdade.
2. **Timestamp sem fuso / hora local** → horário errado em produção e em relatório → `timestamptz` em UTC, converter na borda.
3. **Soft delete sem filtro global** → dado "apagado" aparece em relatório e em API → índice parcial + filtro em todos os acessos (ou view/RLS).
4. **`SELECT *` em tabela larga** → I/O e memória desnecessários, contrato acidental → colunas explícitas.
5. **FK sem índice** → delete/update do pai trava a tabela filha → índice na coluna de FK.
6. **`UNIQUE` global em tabela multi-tenant** → cliente A bloqueia e-mail de cliente B → `(tenant_id, email)`.
7. **`jsonb` sem schema** → dado inválido entra e quebra o consumidor → validação de schema + check quando possível.
8. **Enum como string livre** → valor inválido em produção → enum/tabela de domínio.
9. **`DELETE` gigante em produção** → lock longo, WAL explosivo, réplica atrasada → lotes com pausa + arquivamento.
10. **Contador derivado da tabela inteira a cada request** → full scan em toda listagem → contador materializado ou cache.

## Acesso a dados
11. **N+1** → 1 + N queries por request → join/`IN`/DataLoader; verificar no log de query.
12. **Transação aberta durante chamada HTTP** → conexão presa, lock longo → I/O fora da transação.
13. **Filtro de tenant no código em um lugar só** → uma rota esquece e vaza → filtro na camada de dados/RLS + teste.
14. **Autorização só por rota** → IDOR → checagem por recurso.
15. **`WHERE 1=1` + concatenação "só em filtro"** → injeção → allowlist + parâmetro.
16. **`ORDER BY` com coluna vinda do cliente** → injeção/erro 500 → allowlist de ordenação.
17. **Offset em tabela grande** → varredura de N linhas para página 500 → keyset.

## Contrato
18. **`200` com `{error}` no corpo** → cliente não distingue falha → status correto.
19. **`500` para validação** → alerta falso e cliente sem ação → `400/422` com `code`.
20. **Erro que vaza SQL/tabela/stack** → informação para ataque → mensagem estável + `request_id`.
21. **Campo removido/renomeado sem deprecação** → cliente quebra em produção → versão + janela.
22. **Paginação sem ordenação determinística** → linha duplicada/perdida → tiebreaker por id.
23. **Listagem sem limite máximo** → resposta de 200 MB → limite no servidor.
24. **Contrato documentado à mão e divergente** → doc mentirosa → gerar/validar no CI.

## Concorrência e consistência
25. **Read-modify-write sem lock** → lost update (saldo, estoque) → `SELECT ... FOR UPDATE`, versão otimista ou update atômico (`SET x = x - 1 WHERE x >= 1`).
26. **Efeito colateral sem idempotência** → retry cobra duas vezes → chave de idempotência.
27. **Evento publicado fora da transação** → estado salvo sem evento (ou o contrário) → outbox.
28. **Retry sem backoff/limite** → tempestade de retry derruba o serviço → backoff + jitter + limite + circuit breaker.
29. **Timeout ausente** → thread presa, esgotamento de pool → timeout menor que o do cliente.

## Operação
30. **Migração e deploy na mesma janela sem ordem** → código novo com schema antigo → expand/contract + ordem documentada.
31. **Backfill dentro da migração** → deploy de 40 min com lock → job separado, em lotes.
32. **Log com PII/segredo** → vazamento em coletor de log → mascarar na origem.
33. **Job silencioso sem métrica** → quebrado há semanas → métrica de execução + alerta de atraso.
34. **Cache sem invalidação** → dado velho servido como atual → TTL + versão de chave + evento.
35. **Cache sem tenant na chave** → dado de um cliente servido a outro → chave com tenant.
36. **Backup nunca restaurado** → desastre descoberto no desastre → restore ensaiado com RPO/RTO.
37. **`tenant_id` vindo do body/query** → cliente escolhe o tenant e lê o que quiser → derivar da sessão/token; o payload nunca define escopo.
38. **Modelo ORM exposto direto na API** → mass assignment (cliente grava `role`, `tenant_id`, `is_admin`) e vazamento de campo interno → DTO/serializador com allowlist explícita de entrada e de saída.
39. **Autorização decidida no cliente** → esconder o botão não protege a rota → revalidar no servidor, sempre.

## Como usar esta lista
Na revisão adversarial, percorra a lista e responda para cada item: **não se aplica**, **aplicado**, ou **pendente com risco**. Achado vira issue com severidade de `references/quality-gates.md` — nunca "depois eu vejo".
