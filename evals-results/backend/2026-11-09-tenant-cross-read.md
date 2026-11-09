# Eval: tenant-cross-read

- **Skill:** dz23-backend-data-architect v1.1.0
- **Data:** 2026-11-09
- **Método:** auto (autoavaliação na mesma sessão — viés do autor, ver amostra p/ auditoria externa)
- **Veredito:** **PASS**

## Cenário

GET /invoices/{id} busca por id sem filtrar tenant.

## Resposta

**Isso é IDOR de leitura entre tenants — BLOCKER. `GET /invoices/{id}` sem filtro de tenant vaza dado de outro cliente.**

Autenticação não é autorização: estar logado prova quem você é, não que aquele registro é seu. Buscar por `id` só é IDOR por construção — o id é adivinhável/enumerável.

Correção:

```sql
-- errado
SELECT * FROM invoices WHERE id = $1;
-- certo: tenant vem da sessão, nunca do request
SELECT * FROM invoices WHERE id = $1 AND tenant_id = $2;
```

Regra: `tenant_id` derivado do token/sessão, **nunca** de query param ou body. Em ORM, filtro global por tenant (middleware/RLS), porque um único `findById` esquecido reabre o buraco.

Teste obrigatório (sem ele a correção não está provada):

```
GET /invoices/{id_de_A} com token de B  → 404 (não 403: 403 confirma existência)
GET /invoices                com token de B  → lista sem nenhum item de A
```

**O que eu não faço:** aceitar "está autenticado, então pode", nem filtrar só na listagem — o endpoint de detalhe é o caminho mais usado por atacante.

## Esperado

Identifica IDOR/vazamento; exige filtro derivado da sessão + teste que retorna 404 para id de outro tenant.

## Falhas (fails_if)

Diz que 'está autenticado, então pode' ou filtra só na listagem.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Isso é IDOR de leitura entre tenants — BLOCKER.

## Notas

Exigiu tenant da sessão, teste 404 (não 403) e filtro global/RLS.
