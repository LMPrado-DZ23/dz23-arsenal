# dz23-postgres-prod-preflight

Auditoria de pré-produção para **Postgres e Supabase**: os **10 gates** que decidem se o banco pode ir para
produção — e que a IA costuma deixar abertos.

> O modo de falha que esta skill pega: a IA escreve `ENABLE ROW LEVEL SECURITY`, escreve o endpoint com
> `WHERE user_id = ...`, e o banco continua **contornável** por três caminhos que ninguém testou — o dono da
> tabela, a função `SECURITY DEFINER` e a `service_role`.

## Os 10 gates

| # | Gate | O que a IA deixa passar | Severidade |
|---|---|---|---|
| P1 | `FORCE ROW LEVEL SECURITY` | `ENABLE` não vale para o dono nem para `SECURITY DEFINER` | BLOCKER |
| P2 | `statement_timeout` por conexão/role | sem teto, uma query de IA esgota o pool no pico | BLOCKER |
| P3 | `search_path` fixado nas funções | sequestro de schema; `SECURITY DEFINER` roda o código do atacante | BLOCKER |
| P4 | Integridade no banco (`CHECK`/`NOT NULL`/`UNIQUE`) | validação só no front; saldo negativo, transação duplicada | BLOCKER |
| P5 | View ofuscada para PII | `SELECT` direto em tabela de titulares expõe CPF/e-mail | BLOCKER (LGPD) |
| P6 | `REVOKE CREATE ON SCHEMA public` | role de menor privilégio cria objeto no schema padrão | MAJOR |
| P7 | Restore validado + RTO/RPO numéricos | "temos backup" sem ensaio não é backup | BLOCKER |
| P8 | Trilha de auditoria de leitura | sem log de acesso não se mede o escopo de um vazamento | MAJOR |
| P9 | RLS tabela por tabela | tabela nova nasce sem RLS e expõe tudo | BLOCKER |
| P10 | Segregação de credencial | `service_role`/`anon` no cliente = controle total | BLOCKER |

## Como usar

```bash
# 1. só o SQL (não conecta em nada)
python scripts/pg_preflight.py --dry-run

# 2. contra um banco, somente leitura (transação READ ONLY)
python scripts/pg_preflight.py --dsn "$DATABASE_URL_READONLY"
python scripts/pg_preflight.py --dsn "$URL" --only P1,P9
python scripts/pg_preflight.py --dsn "$URL" --json
```

Sem `psql` no PATH o script sai com `2` e instrução — e `--dry-run` continua funcionando.

## Regra central

**Gate sem consulta anexada é `NOT_TESTED`, não `PASS`.** Por isso o script marca `MANUAL` os gates de processo
(P7 restore, P8 política de auditoria, parte externa de P10) em vez de fabricar resultado.

## O que esta skill NÃO faz

- Não aplica DDL/DCL sozinha: `templates/remediation.sql` tem a correção **com rollback** ao lado, para revisão e
  janela.
- Não substitui pentest nem revisão de código: cobre a camada de **banco** (política, privilégio, integridade,
  recuperação, auditoria).
- Não opina sobre modelagem/algoritmo (índice, N+1, particionamento) — isso é
  `dz23-performance-scalability-engine` e `dz23-backend-data-architect`.

## Estrutura

```
SKILL.md                        método, workflow, os 10 gates, vereditos
VERSION / CHANGELOG.md          versionamento
references/10-gates.md          falha + consulta + correção + PASS por gate
references/rls-and-roles.md     3 portas do RLS, policy por tenant, search_path, view de PII
references/backup-and-audit.md  RTO/RPO, ensaio de restore, auditoria append-only
references/supabase-notes.md    anon vs service_role, claims, Realtime/Storage
templates/preflight-report.md   relatório de pré-deploy
templates/remediation.sql       correções com rollback
scripts/pg_preflight.py         executa as consultas (read-only) ou imprime o SQL
scripts/validate_skill.py       valida a própria skill
evals/evals.json                13 casos (1 por gate + 3 de honestidade)
```

## Arsenal — resumo operacional

| Campo | Valor |
|---|---|
| Versão | 1.0.0 |
| Comando | `/dz23-postgres-prod-preflight` |
| Carrega junto | `dz23-backend-data-architect` (implementação), `security-review` (AppSec de código), `dz23-devops-cloud-deployer` (deploy/rollback) |
| Quando usar | antes de subir banco novo, endpoint financeiro, multi-tenant, ou qualquer deploy que toque schema, RLS, papel ou credencial |
| Pré-requisitos | `psql` no PATH e um DSN **read-only** (opcional: sem DSN, o `--dry-run` entrega o SQL) |
| Evidência esperada | saída de cada consulta colada no relatório; `NOT_TESTED` declarado quando não houver execução |
| Não faz | DDL/DCL autônomo, pentest de aplicação, tuning de query |
| Veredito | `PASS` / `PARTIAL` / `FAIL` / `NOT_TESTED` / `BLOCKED_BY_EXTERNAL_DEPENDENCY` |
