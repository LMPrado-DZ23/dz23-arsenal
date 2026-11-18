# Changelog — dz23-backend-data-architect

## [1.1.2] — 2026-11-18

### Adicionado
- Dez conceitos de seguranca de migracao que a referencia nao tinha, destilados do ECC (`database-migrations`, MIT lido no arquivo LICENSE): lock diferente de rewrite, migração aplicada imutavel, forward-only em producao, DDL separado de DML, teste com volume real, drenar writers antigos antes do backfill, validar paridade antes do cutover de leitura, `IS DISTINCT FROM` como predicado de reconciliacao e `FOR UPDATE SKIP LOCKED` por lote.
- `examples/postgres-add-column.sql` e `examples/postgres-column-rename.sql`: exemplos autoverificaveis (tabela temporaria, `RAISE EXCEPTION`, ROLLBACK no fim). Executados nesta maquina contra Postgres 17.11: 7 assercoes PASS, exit 0, zero residuo no banco.

### Corrigido
- A tabela de operacoes recomendava `CREATE INDEX CONCURRENTLY` sem avisar que ele **falha dentro de transacao** -- detalhe que faz a migracao quebrar na ferramenta, nao no banco. Agora documentado, com o motivo pelo qual wrappers transacionais (Django, Prisma, golang-migrate) precisam de escape explicito.

## [1.1.1] — 2026-11-17

### Corrigido
- `scripts/validate_skill.py` não usa mais `assert` para reportar falha das checagens comuns. Sob `python -O` a instrução é removida pelo interpretador e o validador imprimia OK com referência quebrada, saindo 0 — verificado nas dez skills desta data. Agora imprime cada erro em stderr e sai 1 nos dois modos.
- Reprodução: injetar ``Ver `references/quebrada-O-teste.md`.`` no SKILL.md e rodar `python -O scripts/validate_skill.py` → antes exit 0, agora exit 1. Coberto por caso permanente em `scripts/selftest-ferramentas.py` (grupo `rejeicao`).

## [1.1.0] — 2026-11-08

### Adicionado
- `references/threat-modeling-and-appsec.md` — fecha o gap de **AppSec ofensivo** que estava disperso:
  - threat model em 6 passos (fluxo → fronteiras de confiança → STRIDE por elemento → rank → controle → teste)
  - tabela **STRIDE** com pergunta objetiva, controle e teste de verificação por ameaça
  - **OWASP Top 10 → controle verificável**, com evidência exigida por linha
  - **ASVS**: L2 como alvo para SaaS que trata dado de cliente
  - segredos (gitleaks/trivy secret), dependências (scan bloqueando CRITICAL/HIGH), upload (magic bytes)
  - hardening mínimo: CORS, headers, rate limit, payload, timeout, debug, sessão
  - **gates de AppSec que bloqueiam merge**, cada um com a evidência que o sustenta

### Corrigido
- Segurança estava coberta só em `security-and-tenancy.md` (autorização, IDOR, injeção, RLS, LGPD) — faltava
  a camada de **modelagem de ameaças** e o mapeamento OWASP/ASVS. Agora as duas convivem: uma diz *o que
  proteger*, a outra *como provar que está protegido*.

## [1.0.1] — 2026-11-08

### Adicionado
- `references/api-contracts.md`: nota de compliance RFC 9457 (extensões
  permitidas `code`/`request_id`/`fields`).

### Corrigido
- Divergência entre zip `b7ae9e53…bd4a` (v1.0.0) e disco pós-nota.
  O zip v1.0.1 substitui o anterior; o `b7ae9e53` fica marcado como
  histórico e não deve circular.

## [1.0.0] — 2026-11-08

Primeira versão distribuível, sintetizada de 3 fontes (skill base + Gemini + ChatGPT).

### Adicionado
- Tabela de tipos (UUIDv7, BIGINT/NUMERIC(19,4), TIMESTAMPTZ, `created_at`/`updated_at`) — de Gemini
- Envelope de erro e tabela de contraste HTTP (400 × 422, 401 × 403, 404 × 403) — de Gemini
- 4 gotchas concretos: `0.1 + 0.2 ≠ 0.3`, `tenant_id` do body, ORM exposto na API, transação aberta em HTTP externo — de Gemini
- OWASP API Security Top 10 (2023) explícito com checklist por categoria — de ChatGPT
- Seção Supabase (`auth.uid()`, `search_path`, `SECURITY DEFINER`, roles, RLS coverage) — de ChatGPT

### Base
- `SKILL.md`: missão, precedência, método em 9 etapas (AUDIT → DELIVER) e módulo 5 com 6 decisões
  estruturais (fronteiras, persistência, multi-tenancy, migração zero-downtime, segurança, performance/observabilidade).
- 9 references, 2 templates (ADR e revisão de contrato) e validador documental.
- 39 anti-padrões com sintoma, dano e correção.
- Quality gates com severidade BLOCKER/MAJOR/MINOR e matriz de teste por componente.

### Corrigido
- Referência de skill de UI padronizada em `dz23-ultimate-pro-max` (a skill de UI anterior foi substituída).
