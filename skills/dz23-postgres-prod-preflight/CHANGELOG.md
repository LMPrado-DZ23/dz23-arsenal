# CHANGELOG — dz23-postgres-prod-preflight

Todas as mudanças relevantes desta skill. Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
versionamento semântico.

## [1.1.0] — 2026-11-10

**A v1.0.0 nunca tinha rodado contra um Postgres de verdade.** Nesta versão o script foi executado num
`postgres:16-alpine` com dois cenários — banco limpo (controle positivo) e banco com defeitos (controle
negativo) — e **cinco defeitos reais** apareceram no próprio instrumento.

### Corrigido (defeitos encontrados na execução real)

1. **`READ ONLY` era decorativo.** O script rodava `-c "SET TRANSACTION READ ONLY;"` como comando solto; o
   Postgres emite `WARNING: SET TRANSACTION can only be used in transaction blocks` e **não aplica** o
   read-only. Agora cada consulta roda em `BEGIN READ ONLY; … ROLLBACK;` — o bloco é explícito.
2. **`0 linhas = PASS` para todos os gates estava errado.** P2, P6, P8 e P10 devolvem linha mesmo em banco
   sadio (uma linha por role, uma linha com o ACL, uma com o resumo de auditoria). O resultado era **FAIL
   falso em banco correto**. Agora cada gate tem regra de veredito própria: `rows`, `contagem` (consulta
   escalar, 0 = PASS) ou `manual`.
3. **P5 acusava a própria view de máscara.** O filtro casava `titular_publico` por regex de nome; o alvo
   correto (view ofuscada) aparecia como vazamento. Agora só considera tabela base (`relkind='r'`).
4. **P2 e P10 contavam `postgres`.** Superuser não é "role de aplicação". P2 passou a exigir
   `NOT rolsuper`; P10 só conta role de login **não-superuser** com `BYPASSRLS`.
5. **P6 reprovava PG 15+ por padrão.** Desde o PG 15, `public` já nasce sem `CREATE` para `PUBLIC`; ACL
   `NULL` deixou de ser sinal de falha nessa versão. A regra passou a considerar `server_version_num`.

### Adicionado
- **`--docker <container>`** — roda via `docker exec … psql`, para máquina sem cliente Postgres (foi como a
  verificação desta versão aconteceu).
- **Coluna `escopo`** no relatório: `banco` (RLS, tabela, grants) vs `cluster` (roles, config, backup). Roles
  e `statement_timeout` são **globais** — antes o leitor não sabia que P2/P7/P10 enxergam o cluster inteiro.
- **Contador de infratores** vem do veredito (contagem de falhas), não do número de linhas de evidência.
- Filtro de ruído do psql (`WARNING/NOTICE/HINT`) — antes a linha de aviso era contada como infrator.

### Verificado (evidência desta versão)
| Cenário | Resultado |
|---|---|
| Banco limpo (`betok`): FORCE RLS, policy por tenant, timeout por role, `search_path` fixo, `CHECK` no saldo, view de PII, auditoria, sem `CREATE` em public, sem role com `BYPASSRLS` | **9 PASS automáticos + P7 MANUAL · exit 0** |
| Banco com defeitos (`betbad`): RLS sem FORCE e sem policy, função `SECURITY DEFINER` sem `search_path`, `float` em saldo, PII com grant direto, `CREATE ON public`, sem auditoria, role com `BYPASSRLS` | **9 FAIL · exit 1 · BLOCKER: P1,P2,P3,P4,P5,P9,P10** |

Executado em `postgres:16-alpine` (Docker 29.9.2), container descartado depois do teste.

### Ainda não verificado
- **Os 13 evals não foram executados** (a skill continua `NOT_TESTED` em comportamento).
- Sem teste em Supabase real (o JWT/`auth.uid()` e o painel rodando como superuser seguem teóricos).
- Sem teste em PG < 15 (onde ACL `NULL` em `public` ainda é permissivo).

## [1.0.0] — 2026-11-10

### Adicionado
- Skill nova: auditoria de pré-produção para **Postgres e Supabase** com **10 gates** de segurança e
  integridade, derivados das 10 falhas que a IA mais deixa no banco antes de subir.
- `references/10-gates.md` — para cada gate: a falha, a consulta de detecção, a correção e o critério de PASS.
- `references/rls-and-roles.md` — as três portas do RLS (dono, `SECURITY DEFINER`, `BYPASSRLS`), role por
  função, policy por tenant, teste de contorno com três consultas, sequestro de `search_path`, view de PII
  com `security_barrier`.
- `references/backup-and-audit.md` — RTO/RPO em número, registro mínimo de ensaio de restore, tabela de
  auditoria append-only, custo de `pgaudit` vs log de statement.
- `references/supabase-notes.md` — `anon` vs `service_role`, `auth.uid()`/claims, Realtime e Storage.
- `templates/preflight-report.md` — relatório de pré-deploy com evidência por gate e veredito.
- `templates/remediation.sql` — correção por gate com **rollback ao lado**.
- `scripts/pg_preflight.py` — consultas read-only; `--dry-run`; gates de processo como `MANUAL`.
- `scripts/validate_skill.py` — valida estrutura, frontmatter, VERSION, CHANGELOG e schema dos evals.
- `evals/evals.json` — **13 casos** (um por gate + 3 de honestidade), todos reasoning-only.
