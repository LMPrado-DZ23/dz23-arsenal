# Track B — evals bloqueados por infraestrutura

**40 evals** não podem ser executados nesta máquina. Não é falha de método: cada um exige
uma dependência que não existe aqui. Declarar é mais honesto que simular.

| Skill | Eval | Categoria | Dependência que falta |
|---|---|---|---|
| backend | `n-plus-1` | B | Postgres com volume realista + log de query |
| devops | `no-observability-after-release` | B | release real com observabilidade |
| devops | `prod-deploy-without-approval` | A | pipeline e ambiente de deploy reais |
| devops | `rollout-without-deadline` | B | orquestrador real (K8s/ECS) |
| e2e | `auth-bypass-not-tested` | A | app com autenticação real |
| e2e | `click-before-hydration` | B | app SSR/hidratando real |
| e2e | `flaky-quarantine` | B | Playwright com teste intermitente real |
| e2e | `fragile-selector` | B | Playwright com app rodando |
| e2e | `missing-trace-evidence` | A | CI com upload de artifact |
| e2e | `mock-own-backend` | B | Playwright com app real vs mock |
| e2e | `production-destructive` | A | ambiente de produção (não executável com segurança) |
| e2e | `secret-in-repo` | A | repositório com histórico e Docker real |
| e2e | `shared-user-state` | B | Playwright com suíte de 2+ testes |
| e2e | `sleep-instead-of-wait` | B | Playwright com app rodando |
| e2e | `sync-assertion-vs-async` | B | Playwright com elemento que aparece com atraso |
| e2e | `tenant-cross-read-not-tested` | A | app multi-tenant rodando com 2 usuários |
| e2e | `test-passing-without-assertion` | A | Playwright com app rodando |
| e2e | `visual-baseline-auto-update` | B | Playwright com baseline visual |
| performance | `average-instead-of-percentile` | B | medição real com volume (RUM ou load test) |
| performance | `budget-missing` | B | baseline medido do projeto-alvo |
| performance | `cache-without-invalidation` | B | cache real (Redis) ou proxy com cache |
| performance | `claims-faster-without-command` | B | benchmark antes/depois do projeto-alvo |
| performance | `compression-on-media` | B | servidor HTTP real com Brotli/GZIP habilitado |
| performance | `glass-and-cache` | B | servidor HTTP real para inspecionar headers |
| performance | `index-without-explain` | B | Postgres com volume realista (`EXPLAIN ANALYZE, BUFFERS`) |
| performance | `layers-swapped` | B | trace/waterfall de projeto real |
| performance | `mobile-untested` | C | browser com throttle de rede e CPU (Playwright) ou device real |
| performance | `no-regression-guard` | A | pipeline CI do projeto-alvo (Lighthouse CI / budget check) |
| performance | `offset-pagination` | A | Postgres com tabela grande para medir degradação do OFFSET |
| performance | `timeout-missing` | B | dependência externa real (ou stub que atrase de propósito) |
| reverse-engineer | `coverage-fake` | B | conjunto real de 500 binários |
| reverse-engineer | `emulation-blamed` | B | qemu + imagem de firmware real |
| reverse-engineer | `encrypted-without-proof` | A | imagem de firmware real com bloco cifrado |
| reverse-engineer | `extension-as-truth` | B | arquivo real de formato desconhecido |
| reverse-engineer | `flash-without-backup` | A | hardware (não executável — risco físico) |
| reverse-engineer | `hardware-voltages` | A | hardware + multímetro |
| reverse-engineer | `run-on-host` | A | VM/container descartável |
| reverse-engineer | `signed-as-encrypted` | B | imagem FIT assinada real |
| reverse-engineer | `single-dump` | B | hardware com flash acessível (ou 2 dumps reais) |
| reverse-engineer | `whole-file-as-rootfs` | B | imagem de firmware real com squashfs |

## O que isso significa para a cobertura

- Críticos (categoria A) que **exigem** infra: 13
- Críticos executáveis sem infra: 45 − 13 = 32

Ou seja: **100% dos críticos não é atingível neste ambiente**. O número honesto é
**32/45 (71%)** de críticos executados, com os demais declarados
`BLOCKED_BY_EXTERNAL_DEPENDENCY`.

## Para desbloquear (ordem de custo/benefício)

| Dependência | Desbloqueia | Custo |
|---|---|---|
| **Postgres em Docker** | `index-without-explain`, `n-plus-1`, `offset-pagination` | baixo (imagem + dataset) |
| **Playwright + app de teste** | 9 evals de e2e | médio (app precisa existir) |
| **Servidor HTTP local** | headers de cache/compressão | baixo |
| **Ghidra 12.1.x** | desmontagem do REA (PE) | médio (~500 MB + JDK) |
| **Hardware** | 4 evals de flash/tensão | alto (risco físico — não recomendado só para eval) |
