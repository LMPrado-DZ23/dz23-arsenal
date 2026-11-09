# Eval: webhook-replay

- **Skill:** dz23-backend-data-architect v1.1.0
- **Data:** 2026-11-09
- **Método:** auto-then-reaudit (autoavaliação + releitura adversarial do mesmo autor)
- **Veredito:** **PASS**

## Cenário

Webhook de provedor chega duas vezes com o mesmo event_id.

## Resposta

**Webhook com o mesmo `event_id` duas vezes é retry normal do provedor, não bug dele. Deduplico por `event_id` na mesma transação do efeito.**

Provedor reenvia quando não recebe 2xx a tempo — e você pode receber o mesmo evento 3× por timeout, deploy ou retry de infra. Sem dedupe, o efeito acontece três vezes (cobrança, estoque, e-mail).

```
BEGIN;
  INSERT INTO webhook_events (event_id, provider, payload_hash, received_at)
    VALUES ($1, $2, $3, now())
    ON CONFLICT (event_id) DO NOTHING
    RETURNING id;
  -- se nada foi inserido: evento já processado
  --   → responder 200 (não é erro) e sair, sem repetir o efeito
  ... aplicar o efeito (idempotente) no mesmo commit ...
COMMIT;
```

Regras: `UNIQUE(event_id)` é a garantia (não o `SELECT` antes); responder `200` em duplicata (senão o provedor reenvia para sempre); guardar `payload_hash` (mesmo `event_id` com payload diferente é incidente, não duplicata); retenção de 30–90 dias.

**O que eu não faço:** processar duas vezes, nem "consertar apagando o efeito". Consertar depois é pior: o efeito já saiu para o cliente e o log não prova qual foi o primeiro.

## Esperado

Deduplica por event_id, efeito idempotente, registro do processamento na mesma transação.

## Falhas (fails_if)

Processa duas vezes ou 'conserta' apagando o efeito.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Webhook com o mesmo `event_id` duas vezes é retry normal do provedor, não bug dele.

## Notas

Re-leitura adversarial: nenhum
