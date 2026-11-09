# Contratos de API

## Contrato antes do código
Um endpoint é um acordo público. Antes de implementar, escreva: recurso, verbo, caminho, autenticação, autorização por recurso, payload de entrada, payload de saída, códigos de status, formato de erro, paginação, idempotência, limites e política de versionamento. Sem isso, o cliente define o contrato por tentativa e erro.

## REST
- Recurso no plural, `snake_case` ou `camelCase` — escolha uma e mantenha: `/api/v1/orders/{id}/items`.
- V erbo com significado: `GET` (seguro), `POST` (cria/executa), `PUT` (substitui), `PATCH` (altera parcial), `DELETE` (remove). `POST` para ação não-CRUD: `/orders/{id}/cancel`.
- Status: `200` leitura/atualização, `201` + `Location` criação, `204` sem corpo, `400` payload inválido, `401` não autenticado, `403` autenticado sem permissão, `404` inexistente **ou** invisível ao usuário (não vaze existência), `409` conflito de estado, `422` regra de negócio violada, `429` com `Retry-After`, `5xx` só para falha inesperada.
- Nunca `200` com `{error: ...}` dentro. Nunca `500` para validação.

## Erros
Formato estável e documentado (RFC 9457 `application/problem+json` ou padrão do projeto):
```json
{"type":"https://api.exemplo/problems/insufficient-balance","title":"Saldo insuficiente",
 "status":422,"code":"insufficient_balance","detail":"Saldo disponível: 150,00","request_id":"01J...",
 "fields":[{"name":"amount","reason":"greater_than_available"}]}
```
- Código de erro estável para o cliente programar (`code`), mensagem para humano (`detail`).

> `code`, `request_id` e `fields` são extensões permitidas pelo RFC 9457
> (qualquer membro adicional é legal). O `type` (URI) identifica o
> problema; o `code` (string estável) identifica o caso de negócio.
> Clientes não devem parsear `detail` para decidir.

### 400 vs 422 · 401 vs 403 · 404 vs 403
| Par | Regra |
|---|---|
| `400` × `422` | `400` = requisição malformada (JSON inválido, tipo errado, campo obrigatório ausente). `422` = sintaxe válida, semântica de negócio recusada (saldo insuficiente, estado incompatível, transição proibida). |
| `401` × `403` | `401` = não autenticado (sem credencial, token expirado) → cliente deve autenticar. `403` = autenticado, mas sem permissão para esta ação → cliente não resolve logando de novo. |
| `404` × `403` | Recurso de outro usuário/tenant retorna **`404`** para não confirmar existência. `403` só quando o recurso é público e a ação é que falta. |
| `409` | Conflito de estado/unicidade/versão (edição concorrente, chave duplicada). |
| `429` | Limite de taxa, com `Retry-After`. Nunca `503` para rate limit. |
- Nunca exponha stack, SQL, nome de tabela, caminho interno ou segredo.
- `request_id` em toda resposta e em todo log — é o que liga o relato do usuário à linha de log.

## Paginação e listagem
| Cenário | Escolha |
|---|---|
| Conjunto pequeno e estável | offset (`?page=&per_page=`) |
| Volume, feed, tabela grande | keyset/cursor (`?cursor=&limit=`) — estável sob inserção |
| Exportação | job assíncrono + link, nunca listar tudo na request |
Toda listagem tem `limit` máximo no servidor (ex.: 100) e ordenação determinística (sempre um tiebreaker por id). Sem ordenação estável, paginação duplica e perde linha.

## Filtros, ordenação e busca
Nomeados e validados por allowlist (`?status=paid&sort=-created_at`). Nunca interpole nome de coluna vindo do cliente — mapeie para allowlist. Busca textual com índice adequado (`tsvector`, trigram) e limite de termos.

## Idempotência
`Idempotency-Key` em `POST` com efeito colateral. Mesma chave + mesmo payload → mesma resposta; mesma chave + payload diferente → `409`. TTL documentado.

## Versionamento e mudança
- Versão no caminho (`/v1`) ou header — uma escolha, documentada.
- **Aditivo é seguro**: novo campo opcional, novo endpoint, novo enum aceito. **Breaking**: remover campo, mudar tipo, tornar obrigatório, mudar semântica, mudar código de erro.
- Breaking change: anuncie deprecação, mantenha as duas versões por janela definida, instrumente uso da versão antiga, remova só com evidência de consumo zero.
- Campo removido não é reaproveitado com outro significado.

## GraphQL
Schema versionado por evolução (deprecação com `@deprecated`), `DataLoader` obrigatório para evitar N+1, limite de profundidade e complexidade, paginação por conexão (Relay), erro em `errors` com `extensions.code`, mutação com `clientMutationId` para idempotência.

## gRPC / protobuf
- `reserved` para campos removidos; nunca reutilize número de campo.
- Compatibilidade: adicionar campo é seguro; mudar tipo não é.
- Erro com `google.rpc.Status` e detalhes tipados.

## Eventos
Envelope estável: `event_id`, `type`, `version`, `occurred_at`, `producer`, `tenant_id`, `correlation_id`, `payload`. Schema versionado; consumidor tolera campo novo (ignora desconhecido). Evento é fato no passado — nome no passado (`order.created`), payload imutável.

## Documentação
OpenAPI/AsyncAPI versionado no repositório, gerado ou validado no CI. Contrato sem teste de contrato é documentação morta: adicione teste que valide request/response contra o schema.

## Critério de saída do contrato
(a) OpenAPI/AsyncAPI atualizado; (b) exemplos de request e resposta de sucesso e de erro; (c) matriz de status; (d) teste de contrato passando; (e) declaração explícita de breaking change (ou "nenhuma").
