# Contratos de interface

## Por que antes de paralelizar
Duas pessoas (ou dois agentes) implementando lados opostos de uma integração sem contrato escrito produzem
retrabalho garantido. O contrato é o que permite trabalhar em paralelo sem se falar a cada hora.

## O que o contrato define
| Campo | Exemplo |
|---|---|
| Nome e versão | `orders.create@v1` |
| Entrada | `{customer_id, items[], coupon?}` com tipos e limites |
| Saída de sucesso | `201 {id, status, total_cents}` |
| Erros | `400 invalid_payload`, `409 duplicate`, `422 out_of_stock` |
| Semântica | idempotência, ordenação, consistência, quem é dono do dado |
| Não funcional | timeout, tamanho máximo, paginação, rate limit |
| Compatibilidade | o que pode mudar sem quebrar; como versionar |

## Formas de contrato
- **API REST/GraphQL/RPC**: schema (OpenAPI/proto) versionado no repositório.
- **Evento**: nome no passado, envelope com `id`, `type`, `version`, payload imutável.
- **Função/módulo interno**: assinatura, tipos, erros e invariantes.
- **Dado**: tabela, colunas, chave, semântica de nulo e dono da escrita.

Detalhe de API aprofundado fica em `api-and-contracts` / `dz23-backend-data-architect`; aqui o objetivo é
**fechar o suficiente para destravar o paralelo**.

## Regras
- Contrato sem consumidor declarado é especulação — não escreva.
- Contrato cobre **erro, timeout e vazio**, não só o caminho feliz.
- Mudança aditiva é segura; remoção/mudança de tipo exige versão e janela.
- Contrato é código: versionado, revisado e testado (teste de contrato).
- Quem consome não inventa campo; quem produz não remove campo sem aviso.

## Template curto
```
## CONTRATO: export.orders@v1 (fecha 2026-11-10)
Entrada: {from: date, to: date, format: 'csv'}   | máx 366 dias
Sucesso: 200 text/csv, header fixo, uma linha por pedido
Erros: 400 período inválido · 403 sem permissão · 429 > 5 req/min
Semântica: valores em pt-BR; timezone America/Sao_Paulo; pedido cancelado incluído com status
Compatibilidade: adicionar coluna ao final é seguro; renomear exige v2
Dono: time pedidos · Consumidor: fatia SL-04
```

## OpenAPI 3.1 mínimo
```yaml
openapi: 3.1.0
info: {title: <serviço>, version: 1.0.0}
paths:
  /api/v1/orders/{id}:
    get:
      summary: Consulta pedido do tenant da sessão
      parameters:
        - {name: id, in: path, required: true, schema: {type: string, format: uuid}}
        - {name: Idempotency-Key, in: header, required: false, schema: {type: string}}
      responses:
        '200': {description: OK, content: {application/json: {schema: {$ref: '#/components/schemas/Order'}}}}
        '401': {$ref: '#/components/responses/Unauthorized'}
        '404': {$ref: '#/components/responses/NotFound'}
        '429': {$ref: '#/components/responses/TooManyRequests'}
components:
  responses:
    Unauthorized: {description: sem sessão}
    NotFound: {description: inexistente ou de outro tenant}
    TooManyRequests:
      description: rate limit
      headers: {Retry-After: {schema: {type: integer}}}
```

## Códigos HTTP — semântica
| Código | Quando | Nunca |
|---|---|---|
| `400` | requisição malformada (JSON inválido, tipo errado, campo obrigatório ausente) | usar para regra de negócio |
| `422` | sintaxe válida, semântica recusada (estado incompatível, saldo, regra) | usar para payload quebrado |
| `401` | sem sessão/token expirado | usar para falta de permissão |
| `403` | autenticado sem permissão na ação | devolver para recurso de outro tenant |
| `404` | inexistente **ou de outro tenant** (não confirme existência) | `403` que revela que o recurso existe |
| `409` | conflito de estado/unicidade/versão | usar para validação de campo |
| `429` | rate limit, com `Retry-After` | `503` para limite de taxa |

## Envelope de erro (RFC 9457)
```json
{"type":"https://api.exemplo/problems/slot-taken","title":"Horário indisponível",
 "status":409,"code":"slot_taken","detail":"O horário 14:00 já está reservado",
 "request_id":"01J...","fields":[{"name":"slot","reason":"already_booked"}]}
```
`code` é estável para o cliente programar; `detail` é para humano. Nunca exponha stack, SQL ou tabela.

## Idempotência
`Idempotency-Key` em `POST` com efeito colateral. Mesma chave + mesmo payload → mesma resposta; mesma chave
+ payload diferente → `409`. TTL declarado. Webhook: deduplica por `event_id` do provedor.

## Rate limit
Por identidade correta (token/usuário autenticado), não só por IP — IP é spoofável e compartilhado atrás de
NAT. Limite por rota cara e por login; resposta `429` com `Retry-After` e headers de quota.

## Paginação
Offset só em conjunto pequeno e estável; **keyset/cursor** em volume. Teto no servidor (ex.: 100),
ordenação determinística com tiebreaker por id.

## Saída
Um contrato por fronteira paralela, com dono, consumidor, versão e critério de compatibilidade.
