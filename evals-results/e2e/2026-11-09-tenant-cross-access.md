# Eval: tenant-cross-access

- **Skill:** dz23-e2e-browser-verifier v1.1.0
- **Data:** 2026-11-09
- **Método:** auto-then-reaudit (autoavaliação + releitura adversarial do mesmo autor)
- **Veredito:** **PASS**

## Cenário

Usuário do tenant A abre URL de pedido do tenant B e a tela mostra o pedido.

## Resposta

**Isso é vazamento entre tenants — BLOCKER, não bug de UI. Usuário de A abrindo URL de pedido de B e vendo o pedido é IDOR.**

A tela mostrar é só o sintoma visível; a causa é a API entregando dado de outro tenant. Corrigir o frontend (esconder o link) não fecha nada: a URL/API continua respondendo.

```
BLOCKER: leitura cruzada entre tenants
CAUSA ESPERADA: GET /orders/{id} sem filtro de tenant (ou filtro só na listagem)
CORREÇÃO (servidor): WHERE id = $1 AND tenant_id = <da sessão>
TESTE OBRIGATÓRIO (E2E + API):
  - login como A, abrir URL de pedido de B → 404 (não 403: 403 confirma existência)
  - listagem de A não contém nenhum item de B
  - endpoint de API direto (sem UI) responde igual — o teste de UI não basta
```

Regra de resposta: erro de autorização entre tenants é `404` e loga o incidente; `403` revela que o recurso existe.

**O que eu não faço:** tratar como cosmético (esconder no frontend) nem adicionar só teste de listagem. O caminho de ataque é a URL direta; o teste tem que provar que ele está fechado.

## Esperado

Classifica como BLOCKER; exige teste que espere 404/403 e valida que listagem não contém dado de B.

## Falhas (fails_if)

Trata como cosmético ou só adiciona teste de listagem.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Isso é vazamento entre tenants — BLOCKER, não bug de UI.

## Notas

Re-leitura adversarial: nenhum
