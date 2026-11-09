# Eval: pagination-unbounded

- **Skill:** dz23-backend-data-architect v1.1.0
- **Data:** 2026-11-09
- **Método:** auto-then-reaudit (autoavaliação + releitura adversarial do mesmo autor)
- **Veredito:** **PASS**

## Cenário

GET /orders retorna todas as linhas do tenant.

## Resposta

**`GET /orders` sem teto é negação de serviço por design: um cliente pede o tenant inteiro e o servidor tenta servir.**

`?limit=` do cliente não é limite — é sugestão. O servidor precisa de teto próprio e o cliente precisa de paginação determinística.

```
TETO no servidor: limit = min(requested ?? 50, 200)   // 200 nunca é ultrapassado
PAGINAÇÃO: keyset (cursor), não offset
ORDENAÇÃO: campo único e estável + tiebreaker (ex.: created_at DESC, id DESC)
CURSOR: opaco (base64 de created_at+id), assinado ou validado
ÍNDICE: (tenant_id, created_at DESC, id DESC) — cobre filtro + ordem
RESPOSTA: { items, next_cursor } — next_cursor null no fim
```

Offset falha por dois motivos: fica mais lento quanto maior o offset (`OFFSET 100000` varre 100 mil linhas) e pula/duplica item quando algo é inserido entre as páginas. Keyset resolve os dois.

**O que eu não faço:** confiar no `?limit=` do cliente, nem paginar por offset sem teto. Paginação sem ordenação determinística é paginação que mente.

## Esperado

Aplica limite máximo no servidor, paginação por keyset e ordenação determinística com tiebreaker.

## Falhas (fails_if)

Confia no `?limit=` do cliente ou pagina por offset sem teto.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: `GET /orders` sem teto é negação de serviço por design

## Notas

Re-leitura adversarial: menor: fixa teto em 200 sem justificar o valor (é decisão de produto, não regra universal)
