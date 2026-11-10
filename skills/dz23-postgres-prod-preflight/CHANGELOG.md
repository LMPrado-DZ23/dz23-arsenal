# CHANGELOG — dz23-postgres-prod-preflight

Todas as mudanças relevantes desta skill. Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
versionamento semântico.

## [1.0.0] — 2026-11-10

### Adicionado
- Skill nova: auditoria de pré-produção para **Postgres e Supabase** com **10 gates** de segurança e
  integridade, derivados das 10 falhas que a IA mais deixa no banco antes de subir.
- `references/10-gates.md` — para cada gate: a falha, a consulta de detecção, a correção e o critério de PASS.
- `references/rls-and-roles.md` — as três portas do RLS (dono, `SECURITY DEFINER`, `BYPASSRLS`), role por
  função, policy por tenant, teste de contorno com três consultas, seqüestro de `search_path`, view de PII
  com `security_barrier`.
- `references/backup-and-audit.md` — RTO/RPO em número, registro mínimo de ensaio de restore, tabela de
  auditoria append-only, custo de `pgaudit` vs log de statement.
- `references/supabase-notes.md` — `anon` vs `service_role`, `auth.uid()`/claims, Realtime e Storage, migração
  pelo painel roda como superuser e não testa RLS.
- `templates/preflight-report.md` — relatório de pré-deploy com evidência por gate e veredito.
- `templates/remediation.sql` — correção por gate com **rollback ao lado** e cuidado de lock em tabela grande.
- `scripts/pg_preflight.py` — roda as consultas em transação `READ ONLY` via `psql`; `--dry-run` imprime o SQL;
  gate de processo (P7/P8/P10 externo) sai como `MANUAL` em vez de inventar resultado.
- `scripts/validate_skill.py` — valida estrutura, frontmatter, VERSION, CHANGELOG e schema dos evals.
- `evals/evals.json` — **13 casos** (um por gate + 3 de honestidade), todos reasoning-only.

### Decisões de desenho
- **Gate sem consulta = `NOT_TESTED`**, nunca `PASS`. É a regra que a skill usa contra si mesma.
- **P7 (restore) e P8 (auditoria) são `MANUAL`**: dependem de processo e registro, não de uma query. O script
  mostra o que conferir e não fabrica veredito.
- **Nada de DDL no script**: toda consulta é catálogo, em transação read-only.
