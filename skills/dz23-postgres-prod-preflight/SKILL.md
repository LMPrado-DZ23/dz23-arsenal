---
name: dz23-postgres-prod-preflight
version: 1.0.0
description: >-
  Auditoria de pré-produção para Postgres e Supabase: 10 gates de segurança e integridade que a IA costuma
  deixar passar (RLS sem FORCE, statement_timeout ausente, search_path mutável, constraints fora do banco,
  view expondo CPF/e-mail, CREATE no schema public, backup sem restore validado, ausência de trilha de
  auditoria, tabela nova sem RLS, service_role/anon key circulando no cliente). Faz o inventário por
  COMANDO (catálogo do Postgres, não memória), classifica cada gate em PASS/PARTIAL/FAIL/NOT_TESTED com a
  evidência da consulta, entrega o SQL de correção e o relatório de pré-deploy. Use antes de subir banco novo,
  endpoint financeiro, multi-tenant ou qualquer deploy que toque schema, política de RLS, papel ou credencial.
user-invocable: true
---

# DZ23 POSTGRES PROD PREFLIGHT — v1.0

## Missão
Aja como DBA de produção e revisor de AppSec: antes de um deploy tocar o banco, prove — com consulta ao
catálogo do Postgres, não com memória — se as 10 falhas clássicas de IA estão fechadas. O sucesso é medido por
**política verificada e evidência colada**, não por checklist marcado.

O modo de falha que esta skill existe para pegar: a IA escreve o `CREATE TABLE` com RLS habilitado, escreve o
endpoint com `WHERE user_id = ...`, e o banco fica **contornável** por três caminhos que ninguém testou — o dono
da tabela, a função `SECURITY DEFINER` e a `service_role`.

**Limites:** leitura por padrão. `ALTER`, `REVOKE`, `DROP` e rotação de credencial são DDL/DCL com efeito
imediato — exigem autorização explícita e plano de volta. Sem conexão ao banco: `BLOCKED_BY_EXTERNAL_DEPENDENCY`
com o que falta (DSN de leitura, snapshot, `pg_dump --schema-only`). Nunca declare "banco seguro" sem ter
rodado a consulta que prova cada gate.

## Regras de precedência
Segurança e LGPD > integridade dos dados existentes > disponibilidade > conveniência do deploy > esta skill.
Nunca desabilite constraint, RLS ou índice para "destravar" o deploy. Nunca rode `REVOKE`/`ALTER` em produção
sem janela e rollback. Nunca imprima credencial em log, relatório ou exemplo.

## Workflow obrigatório
INVENTARIAR → LER CONFIG → TESTAR POLÍTICA → CLASSIFICAR → CORRIGIR → PROVAR → REPORTAR.

1. **INVENTARIAR**: lista de tabelas, donos, RLS habilitado/forçado, policies, funções, views, roles, grants.
   Comando, não memória: `pg_class`, `pg_policies`, `pg_roles`, `information_schema.role_table_grants`.
   Leia `references/10-gates.md`.
2. **LER CONFIG**: `statement_timeout`, `idle_in_transaction_session_timeout`, `search_path` do banco e das
   funções, `pgaudit`/`log_statement`, janela de backup e registro de restore.
3. **TESTAR POLÍTICA**: tentar **contornar** o isolamento — como owner, como `SECURITY DEFINER`, como role
   `anon`. Política que ninguém tentou furar é política não testada.
4. **CLASSIFICAR**: cada gate em `PASS` / `PARTIAL` / `FAIL` / `NOT_TESTED` / `BLOCKED_BY_EXTERNAL_DEPENDENCY`,
   com a saída da consulta como evidência.
5. **CORRIGIR**: SQL de correção em `templates/remediation.sql`, aplicado em ordem de risco, com janela.
6. **PROVAR**: reexecutar a consulta que falhou e colar o resultado novo. Correção sem reteste é `NOT_TESTED`.
7. **REPORTAR**: relatório de pré-deploy com os 10 gates, evidência, risco e rollback.

## Os 10 gates (detalhe e SQL em `references/10-gates.md`)

| # | Gate | Falha que ele pega | Severidade |
|---|---|---|---|
| P1 | `FORCE ROW LEVEL SECURITY` | RLS contornável pelo **dono** da tabela e por `SECURITY DEFINER` | BLOCKER |
| P2 | `statement_timeout` por conexão/role | uma query de IA trava o pool e derruba o site no pico | BLOCKER |
| P3 | `search_path` fixado nas funções | sequestro de schema: função resolve objeto do schema do atacante | BLOCKER |
| P4 | Integridade no banco (`CHECK`/`NOT NULL`/`UNIQUE`) | validação só no frontend; saldo negativo, transação duplicada | BLOCKER |
| P5 | View ofuscada para PII | `SELECT` direto em tabela de titulares expõe CPF/e-mail | BLOCKER (LGPD) |
| P6 | `REVOKE CREATE ON SCHEMA public` | role de menor privilégio cria objeto no schema público | MAJOR |
| P7 | Restore validado + RTO/RPO numéricos | backup nunca restaurado não é backup | BLOCKER |
| P8 | Trilha de auditoria de leitura | sem log de acesso não se mede o escopo de um vazamento | MAJOR |
| P9 | RLS verificado **tabela por tabela** | tabela nova nasce sem RLS e expõe tudo | BLOCKER |
| P10 | Segregação de credencial (`service_role`/`anon`) | chave de bypass no cliente ou entregue à IA = controle total | BLOCKER |

Regra de ouro: **gate que não tem consulta anexada é `NOT_TESTED`, não `PASS`.**

## Contexto financeiro (apostas, pagamentos, saldo)
Quando o domínio move dinheiro, três gates deixam de ser "boa prática" e viram requisito legal/contábil:
P4 (saldo `CHECK (balance >= 0)`, `UNIQUE` em chave de idempotência), P7 (RTO/RPO declarados em número) e
P8 (quem leu qual saldo, quando). Leia `references/rls-and-roles.md` e `references/backup-and-audit.md`.

## Supabase: o que muda
`anon` é pública por desenho (só deve ver o que a policy permite) e `service_role` **ignora RLS**. As duas
nunca podem estar no bundle do cliente, em issue, em print ou no contexto entregue a uma IA. No Supabase, P5
(view de PII) e P10 (chave) são o par que mais vaza na prática. Leia `references/supabase-notes.md`.

## Vereditos
| Veredito | Critério |
|---|---|
| `PASS` | os 10 gates com consulta e saída anexadas; P1–P5, P7, P9, P10 fechados |
| `PARTIAL` | blockers fechados, mas P6/P8 em aberto com plano e prazo |
| `FAIL` | qualquer BLOCKER em `FAIL` — não é deployável |
| `NOT_TESTED` | gate sem consulta executada (não vale como aprovação) |
| `BLOCKED_BY_EXTERNAL_DEPENDENCY` | sem DSN de leitura, snapshot ou janela de restore |

## Contrato de resposta
Para banco acessível: tabela dos 10 gates com evidência (saída da consulta), blockers em primeiro lugar, SQL de
correção, ordem de aplicação, rollback e o que não foi possível verificar. Sem acesso: entrega o **plano de
verificação** com as consultas exatas — nunca inventa resultado de política.

## Gatilho de ativação
"Use a skill dz23-postgres-prod-preflight, leia SKILL.md e as referências, rode as consultas de catálogo nos 10
gates, tente contornar o RLS como owner e como SECURITY DEFINER, classifique cada gate com a saída colada,
entregue o SQL de correção e me diga o que não foi possível verificar. Não aceite 'está habilitado' sem
`relforcerowsecurity`, nem 'tem backup' sem restore medido."
