# Changelog — dz23-backend-data-architect

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
