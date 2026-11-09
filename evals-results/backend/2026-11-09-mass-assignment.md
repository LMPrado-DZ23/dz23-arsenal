# Eval: mass-assignment

- **Skill:** dz23-backend-data-architect v1.1.0
- **Data:** 2026-11-09
- **Método:** auto-then-reaudit (autoavaliação + releitura adversarial do mesmo autor)
- **Veredito:** **PASS**

## Cenário

PATCH /users recebe o body inteiro e grava direto no modelo.

## Resposta

**`body` inteiro no modelo é mass assignment: o cliente escolhe o que escreve, inclusive `role` e `tenant_id`.**

Validação no frontend não é controle — quem ataca não usa o seu frontend. O servidor precisa de **lista de campos permitidos**, não de lista de proibidos (proibida esquece um campo novo; permitida nunca).

```ts
// errado
await User.update(req.body, { where: { id } });
// certo
const dto = pick(req.body, ['name', 'phone', 'avatar_url']);  // allowlist explícita
await User.update(dto, { where: { id: me.id } });
// role, tenant_id, is_admin: nunca vêm do body — mudam por fluxo próprio, com autorização
```

Teste obrigatório: `PATCH /users` com `{"name":"x","role":"admin","tenant_id":"B"}` →

```
200 somente com name alterado
role continua o mesmo
tenant_id continua o mesmo
(campo proibido: rejeitar 422 ou ignorar silenciosamente — decidir e documentar)
```

**O que eu não faço:** gravar objeto cru, nem "confiar na validação do frontend". O cliente é território do atacante.

## Esperado

Exige DTO/allowlist de campos; bloqueia escrita de role/tenant_id/is_admin; teste de campo proibido.

## Falhas (fails_if)

Grava o objeto cru ou confia na validação do frontend.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: `body` inteiro no modelo é mass assignment: o cliente escolhe o que escreve

## Notas

Re-leitura adversarial: nenhum
