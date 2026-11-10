# Relatório de pré-deploy — banco (Postgres/Supabase)

**Data:** AAAA-MM-DD · **Ambiente:** staging | produção · **Banco:** <nome> · **Versão PG:** <x.y>
**Quem assinou:** <nome> · **Deploy alvo:** <commit/tag>

## Resultado

| # | Gate | Estado | Evidência (consulta/saída) | Bloqueia deploy? |
|---|---|---|---|---|
| P1 | `FORCE RLS` | PASS/PARTIAL/FAIL/NOT_TESTED | `<query>` → `<saída>` | sim |
| P2 | `statement_timeout` | | | sim |
| P3 | `search_path` nas funções | | | sim |
| P4 | Constraints (`CHECK`/`NOT NULL`/`UNIQUE`) | | | sim |
| P5 | View de PII | | | sim |
| P6 | `REVOKE CREATE ON public` | | | não (MAJOR) |
| P7 | Restore validado + RTO/RPO | | | sim |
| P8 | Auditoria de leitura | | | não (MAJOR) |
| P9 | RLS por tabela + teste de contorno | | | sim |
| P10 | Segregação de credencial | | | sim |

**Veredito:** PASS | PARTIAL | FAIL | BLOCKED_BY_EXTERNAL_DEPENDENCY

## Blockers em aberto

| Gate | O que falta | Dono | Prazo | Rollback |
|---|---|---|---|---|

## O que NÃO foi possível verificar

| Item | Motivo (sem DSN / sem janela / sem acesso) |
|---|---|

## Teste de contorno do isolamento (P1 + P9)

```sql
-- como role de runtime, tenant A
SET LOCAL app.tenant_id = '<A>';
SELECT count(*) FROM app.wallet;            -- saída: <n>
-- tenant B tentando ler id de A
SET LOCAL app.tenant_id = '<B>';
SELECT count(*) FROM app.wallet WHERE id = '<id-de-A>';  -- saída: 0
```

## Aplicação das correções

| Ordem | Correção | Janela | Reversível? | Reexecute a consulta |
|---|---|---|---|---|
| 1 | | | | |

## Assinatura

- [ ] Todos os gates com consulta e saída coladas
- [ ] Blockers fechados ou deploy bloqueado
- [ ] Rollback escrito para cada DDL aplicada
- [ ] `NOT_TESTED` declarado, não convertido em PASS
