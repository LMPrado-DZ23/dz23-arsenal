# Checkpoint e retomada

Checkpoint sugerido: `docs/quality-loop/state.md` quando autorizado e adequado ao repositório. Salve a cada 5 ciclos ou antes de ação arriscada/limite de sessão.

```markdown
# Quality Loop State
- Goal: ...
- Status: IN_PROGRESS | BLOCKED | VERIFIED_COMPLETE
- Branch / HEAD: ...
- Working tree baseline: ...
- Cycle: ...
- Last verified time/environment: ...
## Acceptance
| REQ-ID | Gate | Status | Evidence |
## Backlog
| ID | Severity | Repro | Root cause/hypothesis | Attempts | Next action |
## Files changed
## Commands run (with exit code)
## Tests and evidence
## External dependencies / approvals
## Next atomic action
```

## Recuperação segura
1. Confirme diretório, repo, branch, HEAD e diff real; checkpoint é referência, não verdade absoluta.
2. Revalide ambiente, secrets disponíveis (sem exibir), serviços e mudanças de terceiros.
3. Verifique se ações anteriores tiveram efeito antes de repeti-las; exija idempotência para writes e migrações.
4. Repriorize backlog e continue da próxima ação atômica.
5. Se o harness não oferecer retomada automática, reporte `SESSION_LIMIT_REACHED` e forneça comando de retomada, sem alegar execução futura.

## Anti-estagnação
3 tentativas malsucedidas da mesma hipótese exigem nova abordagem; registre evidência e não fique em loop infinito. A contagem de ciclos é um instrumento de observabilidade, não objetivo de produto.
