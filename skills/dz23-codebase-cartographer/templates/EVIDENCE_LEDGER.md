# EVIDENCE_LEDGER — <projeto>

> repo: <path> · commit: <sha> · lido em: <AAAA-MM-DD>
> Regra: nenhuma afirmação sem fonte; nenhuma promoção de `INFERRED` para `VERIFIED` sem evidência nova.

| ID | Afirmação | Fonte | Método | Estado | Gap |
|---|---|---|---|---|---|
| E-001 | Autenticação via JWT | `src/middleware/auth.ts:12` | grep + leitura + teste `auth.test.ts` | VERIFIED | — |
| E-002 | Tenant vem do header da sessão | `src/middleware/tenant.ts:5` | leitura | INFERRED | teste de isolamento não encontrado |
| E-003 | Rate limit ativo | `src/config/rate-limit.ts:9` | grep + leitura | VERIFIED | — |
| E-004 | Soft delete global | — | busca por `deleted_at` | UNKNOWN | não confirmado em todas as tabelas |
| E-005 | LSP/Serena disponível | — | `s.cfg.get_current_config` | BLOCKED_BY_EXTERNAL_DEPENDENCY | sem projeto ativo |

## Estados
- **VERIFIED** — código **+** teste, ou duas fontes independentes.
- **INFERRED** — uma fonte de código, sem teste que confirme.
- **UNKNOWN** — não encontrado; o gap é resultado, não fracasso.
- **BLOCKED_BY_EXTERNAL_DEPENDENCY** — falta ferramenta, credencial ou acesso.

## Gaps
- [ ] Gap-001: <o que falta confirmar> — como confirmar: `<comando>`

## O que este ledger NÃO é
Não é scan de segurança nem prova de runtime. Afirmação `VERIFIED` aqui significa "o código mostra e o teste cobre", não "funciona em produção".
