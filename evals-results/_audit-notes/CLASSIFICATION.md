# Classificação dos evals por criticidade

> Gerado na Rodada 2. **A** = dano direto se violado (segurança, integridade, honestidade). **B** = fluxo certo / anti-pattern. **C** = borda ou cosmético.
> Regra: na dúvida, **A** — segurança primeiro.

| Skill | Eval ID | Categoria | Reasoning? | Track | Estimativa |
|---|---|---|---|---|---|
| autonomous | `loop-infinito` | B | sim | Track A | 15 min |
| autonomous | `hipotese-estagnada` | B | sim | Track A | 15 min |
| autonomous | `quick-seguranca` | B | sim | Track A | 15 min |
| autonomous | `primitive-choice` | B | sim | Track A | 15 min |
| autonomous | `registry-risk` | A | sim | Track A | 20 min |
| autonomous | `visual-proof` | B | sim | Track A | 15 min |
| autonomous | `blocked-secret` | A | sim | Track A | 20 min |
| autonomous | `goal-integration` | B | sim | Track A | 15 min |
| autonomous | `checkpoint-ausente` | A | sim | Track A | 20 min |
| autonomous | `escopo-inflado` | A | sim | Track A | 20 min |
| autonomous | `delegacao-sem-skill` | B | sim | Track A | 15 min |
| backend | `contract-breaking-change` | A | sim | Track A | 20 min |
| backend | `migration-without-rollback` | A | sim | Track A | 20 min |
| backend | `tenant-cross-read` | A | sim | Track A | 20 min |
| backend | `idempotency-missing` | A | sim | Track A | 20 min |
| backend | `n-plus-1` | B | não | Track B (infra) | — |
| backend | `float-for-money` | B | sim | Track A | 15 min |
| backend | `open-transaction-during-http` | A | sim | Track A | 20 min |
| backend | `mass-assignment` | A | sim | Track A | 20 min |
| backend | `webhook-replay` | A | sim | Track A | 20 min |
| backend | `secret-in-log` | A | sim | Track A | 20 min |
| backend | `orm-leaked` | B | sim | Track A | 15 min |
| backend | `pagination-unbounded` | A | sim | Track A | 20 min |
| cartographer | `map-without-commit` | B | sim | Track A | 15 min |
| cartographer | `claim-without-pointer` | A | sim | Track A | 20 min |
| cartographer | `read-everything-claim` | B | sim | Track A | 15 min |
| cartographer | `folder-as-architecture` | B | sim | Track A | 15 min |
| cartographer | `dead-code-guess` | B | sim | Track A | 15 min |
| cartographer | `no-risk-zones` | A | sim | Track A | 20 min |
| cartographer | `blast-radius-vague` | B | sim | Track A | 15 min |
| cartographer | `no-test-area-silent` | A | sim | Track A | 20 min |
| cartographer | `brief-over-budget` | B | sim | Track A | 15 min |
| cartographer | `brief-without-do-not-touch` | B | sim | Track A | 15 min |
| cartographer | `stale-map` | B | sim | Track A | 15 min |
| cartographer | `readme-as-truth` | B | sim | Track A | 15 min |
| cartographer | `two-writers-unnoticed` | B | sim | Track A | 15 min |
| cartographer | `inference-as-fact` | A | sim | Track A | 20 min |
| cartographer | `no-access-honesty` | A | sim | Track A | 20 min |
| devops | `rebuild-per-environment` | B | sim | Track A | 15 min |
| devops | `gate-does-not-block` | B | sim | Track A | 15 min |
| devops | `no-rollback-path` | A | sim | Track A | 20 min |
| devops | `liveness-on-database` | B | sim | Track A | 15 min |
| devops | `no-resource-limits` | B | sim | Track A | 15 min |
| devops | `migration-before-code` | A | sim | Track A | 20 min |
| devops | `admin-credentials-in-ci` | A | sim | Track A | 20 min |
| devops | `replicas-one` | B | sim | Track A | 15 min |
| devops | `backup-never-restored` | A | sim | Track A | 20 min |
| devops | `rollout-without-deadline` | B | não | Track B (infra) | — |
| devops | `prod-deploy-without-approval` | A | não | Track B (infra) | — |
| devops | `no-observability-after-release` | B | não | Track B (infra) | — |
| e2e | `sleep-instead-of-wait` | B | não | Track B (infra) | — |
| e2e | `fragile-selector` | B | não | Track B (infra) | — |
| e2e | `test-passing-without-assertion` | A | não | Track B (infra) | — |
| e2e | `shared-user-state` | B | não | Track B (infra) | — |
| e2e | `tenant-cross-access` | A | sim | Track A | 20 min |
| e2e | `auth-bypass-not-tested` | A | não | Track B (infra) | — |
| e2e | `mock-own-backend` | B | não | Track B (infra) | — |
| e2e | `flaky-quarantine` | B | não | Track B (infra) | — |
| e2e | `missing-trace-evidence` | A | não | Track B (infra) | — |
| e2e | `production-destructive` | A | não | Track B (infra) | — |
| e2e | `secret-in-repo` | A | não | Track B (infra) | — |
| e2e | `visual-baseline-auto-update` | B | não | Track B (infra) | — |
| e2e | `click-before-hydration` | B | não | Track B (infra) | — |
| e2e | `sync-assertion-vs-async` | B | não | Track B (infra) | — |
| e2e | `tenant-cross-read-not-tested` | A | não | Track B (infra) | — |
| performance | `average-instead-of-percentile` | B | não | Track B (infra) | — |
| performance | `layers-swapped` | B | não | Track B (infra) | — |
| performance | `cache-without-invalidation` | B | não | Track B (infra) | — |
| performance | `index-without-explain` | B | não | Track B (infra) | — |
| performance | `one-big-change` | B | sim | Track A | 15 min |
| performance | `timeout-missing` | B | não | Track B (infra) | — |
| performance | `offset-pagination` | A | não | Track B (infra) | — |
| performance | `mobile-untested` | C | não | Track B (infra) | — |
| performance | `budget-missing` | B | não | Track B (infra) | — |
| performance | `glass-and-cache` | B | não | Track B (infra) | — |
| performance | `compression-on-media` | B | não | Track B (infra) | — |
| performance | `no-regression-guard` | A | não | Track B (infra) | — |
| performance | `claims-faster-without-command` | B | não | Track B (infra) | — |
| reverse-engineer | `extension-as-truth` | B | não | Track B (infra) | — |
| reverse-engineer | `encrypted-without-proof` | A | não | Track B (infra) | — |
| reverse-engineer | `run-on-host` | A | não | Track B (infra) | — |
| reverse-engineer | `invented-symbol` | B | sim | Track A | 15 min |
| reverse-engineer | `whole-file-as-rootfs` | B | não | Track B (infra) | — |
| reverse-engineer | `emulation-blamed` | B | não | Track B (infra) | — |
| reverse-engineer | `signed-as-encrypted` | B | não | Track B (infra) | — |
| reverse-engineer | `hardware-voltages` | A | não | Track B (infra) | — |
| reverse-engineer | `single-dump` | B | não | Track B (infra) | — |
| reverse-engineer | `flash-without-backup` | A | não | Track B (infra) | — |
| reverse-engineer | `observed-as-rule` | B | sim | Track A | 15 min |
| reverse-engineer | `coverage-fake` | B | não | Track B (infra) | — |
| spec | `requirement-without-criterion` | A | sim | Track A | 20 min |
| spec | `no-out-of-scope` | A | sim | Track A | 20 min |
| spec | `layer-sliced-plan` | A | sim | Track A | 20 min |
| spec | `parallelize-without-contract` | A | sim | Track A | 20 min |
| spec | `contract-happy-path-only` | B | sim | Track A | 15 min |
| spec | `single-number-estimate` | B | sim | Track A | 15 min |
| spec | `spike-without-question` | B | sim | Track A | 15 min |
| spec | `circular-dependency` | A | sim | Track A | 20 min |
| spec | `done-without-evidence` | A | sim | Track A | 20 min |
| spec | `silent-scope-cut` | A | sim | Track A | 20 min |
| spec | `risky-integration-last` | B | sim | Track A | 15 min |
| spec | `matrix-stale` | B | sim | Track A | 15 min |
| spec | `handoff-without-dod` | B | sim | Track A | 15 min |
| spec | `capacity-100-percent` | B | sim | Track A | 15 min |
| spec | `conflicting-requirements` | A | sim | Track A | 20 min |
| ultimate-pro-max | `tokens-semanticos` | C | sim | Track A | 15 min |
| ultimate-pro-max | `tailwind3` | C | sim | Track A | 15 min |
| ultimate-pro-max | `tailwind4` | C | sim | Track A | 15 min |
| ultimate-pro-max | `estados-interativos` | C | sim | Track A | 15 min |
| ultimate-pro-max | `focus-visible` | C | sim | Track A | 15 min |
| ultimate-pro-max | `reduced-motion` | C | sim | Track A | 15 min |
| ultimate-pro-max | `cls-midia` | B | sim | Track A | 15 min |
| ultimate-pro-max | `shadcn-dono` | C | sim | Track A | 15 min |
| ultimate-pro-max | `badge-wrap` | C | sim | Track A | 15 min |
| ultimate-pro-max | `contraste` | C | sim | Track A | 15 min |
| ultimate-pro-max | `estados-vazio-erro` | C | sim | Track A | 15 min |
| ultimate-pro-max | `prova-visual` | A | sim | Track A | 20 min |
| ultimate-pro-max | `streaming-chat` | B | sim | Track A | 15 min |

## Resumo

- **A (crítico):** 45
- **B (importante):** 62
- **C (borda):** 11
- **Reasoning-only (Track A):** 78
- **Precisam de infra (Track B):** 40

Track C (projeto real) fica vazio nesta rodada: nenhum eval exige produto real para ser julgado.
