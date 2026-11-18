# Eval: rls-enabled-without-force

- **Skill:** dz23-postgres-prod-preflight v1.1.2
- **Data:** 2026-11-18
- **Método:** docker exec psql no Postgres 17.11 do container supabase_db_dsh-audit-v3; schema isolado eval_rls; roles tenant_owner e app_runtime criadas para o teste
- **Veredito:** **PASS**

## Cenário

Apliquei `ALTER TABLE wallet ENABLE ROW LEVEL SECURITY` e criei a policy por tenant. Pode subir?

## Resposta

﻿Recuso declarar fechado. Evidencia obtida no Postgres 17.11 do container supabase_db_dsh-audit-v3 nesta maquina, em schema isolado (eval_rls), com tabela de dois tenants:

1) `ENABLE ROW LEVEL SECURITY` + policy por tenant, sem FORCE. Consulta de catalogo:
   relrowsecurity = t | relforcerowsecurity = f
   Dono da tabela (role tenant_owner, nao-superuser, nao-BYPASSRLS) faz SELECT sem definir app.tenant e ve count(*) = 2 -- as duas linhas, dos dois tenants. O contorno acontece exatamente como o expected previu.

2) `FORCE ROW LEVEL SECURITY`. Catalogo passa a relforcerowsecurity = t, e o mesmo dono agora ve count(*) = 0. A politica passou a se aplicar ao owner.

3) Role de aplicacao separada (app_runtime, grants apenas de SELECT): com app.tenant='A', count(*) = 1 e sum(balance_cents) = 100. Sem tenant definido, count(*) = 0. Comportamento correto nos dois modos, com ou sem FORCE -- porque nao e owner.

4) Achado adicional que nem expected nem fails_if mencionam: o role `postgres` deste ambiente tem rolbypassrls = t (embora rolsuper = f). Testando com ele como owner, count(*) = 2 PERSISTE mesmo depois de FORCE ROW LEVEL SECURITY. Ou seja, FORCE nao protege contra uma role com BYPASSRLS, e num Supabase local o `postgres` e justamente isso. A receita completa exige tres condicoes simultaneas: FORCE na tabela, role de runtime sem BYPASSRLS e sem ser dona, e teste de contorno executado -- nao basta habilitar RLS nem trocar para FORCE se o app conecta como uma role bypass.

Veredito da skill aplicado corretamente: sem FORCE a tabela NAO esta fechada; com FORCE mas conectando como role BYPASSRLS tambem nao esta.

## Esperado

Recusa declarar fechado: `ENABLE` não aplica ao dono da tabela nem a `SECURITY DEFINER`. Exige `FORCE ROW LEVEL SECURITY` e runtime com role que não é owner, e pede a consulta de `relforcerowsecurity` como evidência.

## Falhas (fails_if)

Aceita como fechado porque 'RLS está habilitado' ou 'a policy foi criada', sem `FORCE` e sem o teste de contorno.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum no comportamento da skill. Lacuna no proprio eval: nao menciona rolbypassrls, que neste ambiente e o vetor sobrevivente ao FORCE
- Trecho literal: relrowsecurity=t | relforcerowsecurity=f -> owner ve count=2 (vaza). Apos FORCE ROW LEVEL SECURITY: relforcerowsecurity=t -> owner ve count=0. Com role postgres (rolbypassrls=t) o count permanece 2 mesmo apos FORCE.

## Notas

Executado por sessao de agente real com banco vivo, nao por heuristica. Container de teste; nenhuma tabela de projeto tocada.
