# Eval: contract-happy-path-only

- **Skill:** dz23-spec-to-system-engine v1.2.0
- **Data:** 2026-11-09
- **Método:** auto (autoavaliação na mesma sessão — viés do autor, ver amostra p/ auditoria externa)
- **Veredito:** **PASS**

## Cenário

Contrato define apenas sucesso 200 e o payload.

## Resposta

**Contrato com só 200 não é contrato — é exemplo. Falta o que acontece quando dá errado.**

Quem consome precisa saber o que fazer em cada falha; se não souber, inventa. Inventar erro é como nascem os bugs de integração.

O que falta declarar:

```
400 { code: "invalid_cursor", field: "cursor" }
401 { code: "unauthenticated" }
403 { code: "forbidden", scope: "orders:read" }
404 { code: "not_found" }
409 { code: "conflict", detail: "duplicate idempotency key" }
422 { code: "validation_failed", errors: [{field, message}] }
429 { code: "rate_limited", retry_after_s: 30 }
500 { code: "internal", request_id }
TIMEOUT: cliente 3 s · servidor 2 s
VAZIO: 200 com items: [] e next_cursor: null (não é 404)
COMPATIBILIDADE: campo novo só aditivo; remoção exige deprecação anunciada
PAGINAÇÃO: cursor opaco; mudar ordem invalida cursor antigo
```

Critério de contrato completo: **um cliente consegue implementar sem perguntar nada**.

**O que eu não faço:** considerar completo, nem "documentar os erros depois". Depois = quando o primeiro cliente já tratou errado.

## Esperado

Exige erros (400/403/409/422/429), timeout, vazio e regra de compatibilidade.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Contrato com só 200 não é contrato — é exemplo.

## Notas

Listou 400/401/403/404/409/422/429/500, timeout, vazio e compatibilidade.
