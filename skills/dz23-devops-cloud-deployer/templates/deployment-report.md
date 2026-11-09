# Deploy — <projeto> — <ambiente> — <data>

## Ambiente
- URL:
- Commit SHA:
- Branch:
- Imagem: `<registry>/<app>:<tag>@sha256:<digest>`
- Runtime: K8s | Compose | VPS
- Namespace:
- Janela / aprovador:

## Matriz de evidência
| Etapa | Status | Evidência |
|---|---|---|
| Secrets scan | PASS/PARTIAL/FAIL/NOT_TESTED | security/secrets-scan.json |
| SAST | | security/sast-report.json |
| Build imagem | | security/docker-build.log |
| Scan imagem | | security/trivy-report.json (0 CRITICAL/HIGH) |
| Push registry | | digest sha256:… |
| Terraform plan | | infra/tf-plan.log (+X ~Y -Z) ou N/A |
| Terraform apply | | infra/tf-apply.log ou N/A |
| Migration | | infra/migration.log |
| Rollout | | deploy/rollout.log |
| `/healthz` | | {"status":"ok"} |
| `/readyz` | | {"ready":true,"db":"ok"} |
| Smoke E2E | | deploy/smoke-results.json (N/N) |
| Log rotation | | max-size=10m, max-file=5 |
| Backup recente | | backup/<data>.tar.gz (restore ensaiado) |

> Etapa não executada é `NOT_TESTED`, nunca `PASS`. Ferramenta ausente → `BLOCKED_BY_EXTERNAL_DEPENDENCY`.

## Rollback
- Trigger: <condição>
- Comando: `kubectl rollout undo deployment/app -n <ns>` / `helm rollback app -n <ns>`
- Última versão estável: <digest>
- Tempo esperado: <min>
- Validação: `/healthz` verde + smoke PASS na versão anterior

## Veredito
**PASS | PARTIAL | FAIL | BLOCKED**

## Riscos residuais e próximos passos
- <se PARTIAL/FAIL, o que falta e quem resolve>
- <o que não foi testado>
