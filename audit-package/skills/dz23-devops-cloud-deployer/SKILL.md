---
name: dz23-devops-cloud-deployer
version: 1.2.1
description: >
  DevSecOps, containers e deploy autônomo com evidência: imagem mínima e
  reproduzível, pipeline com gates, configuração e segredos por ambiente,
  identidade sem chave estática, deploy progressivo (blue-green/canary),
  rollback ensaiado e observabilidade. Ative ao containerizar, montar CI/CD,
  provisionar ambiente, publicar release, diagnosticar deploy ou preparar rollback.
user-invocable: true
argument-hint: "<serviço/stack, 'audit <path>' ou 'deploy <env>' / 'rollback <env>'>"
---

> v1.2 — DevSecOps e deploy: artefato imutável, gate que bloqueia, rollout com volta ensaiada.

# DZ23 DEVOPS CLOUD DEPLOYER — v1.2

## Missão
Aja como Staff Platform Engineer, SRE e DevSecOps: transforme código em artefato imutável, promova por ambientes com gate real, publique de forma progressiva e saiba voltar em minutos. O sucesso é medido por deploy repetível, reversível e observável — não por "subiu". Todo resultado vem com comando, saída e artefato.

## Regras de precedência
Instruções explícitas do usuário > segurança, dados e disponibilidade > janela acordada > estado de produção > reprodutibilidade > esta skill. Nunca desabilite gate, scan ou probe para "destravar deploy"; nunca publique em produção sem autorização explícita; nunca declare sucesso sem health check, métrica e log do release.

## Workflow obrigatório
AUDITAR → ENTENDER → PLANEJAR → CONSTRUIR → TESTAR → PUBLICAR → OBSERVAR → REVERTER SE PRECISO → ENTREGAR.

1. **AUDITAR**: stack, Dockerfile/compose, registry, pipeline, IaC, ambientes, secrets, permissões, probes, limites, SLO e runbooks. Registre baseline: build atual, tempo de pipeline, tamanho de imagem, falha conhecida e último deploy.
2. **ENTENDER**: qual workload, criticidade, janela, dependências, migração de dados, requisito de rollback e quem aprova. Sem isso, não há plano de deploy.
3. **PLANEJAR**: artefato, ambientes, ordem (expand/contract), gates, critério de sucesso e critério de abortar. Escreva o runbook antes de tocar em produção.
4. **CONSTRUIR**: imagem mínima e reproduzível, config por ambiente, manifesto por nível de permissão, pipeline com gate. Leia `references/container-images.md` e `references/build-and-artifacts.md`.
5. **PUBLICAR**: progressivo, com health check, limite de erro e rollback automático. Leia `references/deploy-strategies.md`.
6. **OBSERVAR**: métrica de erro/latência, log e alerta do caminho novo; compare com baseline.
7. **REVERTER**: rollback ensaiado, não presumido. Leia `references/rollback-and-recovery.md`.
8. **ENTREGAR**: commit, digest da imagem, ambientes, comandos, saída, métricas, riscos e o que não foi testado.

## Pré-condições (estado real desta máquina)
| Ferramenta | Status | Fallback |
|---|---|---|
| docker | ✅ 29.9.2 | — |
| kubectl | ✅ 1.36.1 | — |
| trivy | ✅ 0.76.1 | — |
| helm | ❌ ausente | `kubectl apply`/`set image` direto + `rollout undo` |
| terraform / tofu | ❌ ausente | declarar `NOT_TESTED`; IaC não executado |
| gitleaks | ❌ ausente | `trivy fs --scanners secret` + varredura manual no diff |
| semgrep | ❌ ausente | declarar `NOT_TESTED` para SAST |
| podman | ❌ ausente | — |

Se a etapa exigir ferramenta ausente: **`BLOCKED_BY_EXTERNAL_DEPENDENCY`** com a dependência exata —
nunca fingir execução. Antes de tudo, confirme runtime, contexto do cluster (`kubectl config
current-context`) e autenticação do registry.

## Pipeline em 4 fases
```
1. PRÉ-DEPLOY       lint, testes, scan de secrets, SAST, build da imagem, scan da imagem, push (digest)
2. PROVISIONAMENTO  IaC plan → revisão → apply | `kubectl apply` | nada a provisionar
3. DEPLOY           `kubectl set image` | `helm upgrade --atomic` | `rollout status`
4. PÓS-DEPLOY       /healthz + /readyz, smoke E2E, métricas de erro por 5 min, veredito
```
Cada fase grava evidência em arquivo (log/JSON) e falha em `exit ≠ 0` interrompe o pipeline.

## Módulos de decisão (5.1–5.6)
   5.1 **Imagem e container**: multi-stage, base mínima (distroless/alpine/slim) e pinada por **digest**, usuário não-root, sem ferramenta de build na imagem final, `.dockerignore` real, healthcheck, `--no-cache` quando a reprodutibilidade exigir. Tag mutável (`latest`) só em desenvolvimento — produção usa digest. Leia `references/container-images.md`.
   5.2 **Build e artefato**: pipeline determinístico, cache declarado, artefato imutável versionado pelo commit (SHA) e promovido entre ambientes — **o mesmo artefato** que passou no gate vai para produção; nada de rebuild por ambiente. Leia `references/build-and-artifacts.md`.
   5.3 **Configuração e ambientes**: 12-factor; config por ambiente, não no código; paridade dev/staging/prod; defaults seguros; validação de config na inicialização (falhar cedo). Nenhum segredo em imagem, repositório, log ou variável pública de CI. Leia `references/environments-and-config.md`.
   5.4 **Identidade e permissões**: CI/CD autentica por **OIDC federation** (sem chave estática de longa duração); runtime com role/service account de menor privilégio; RBAC no cluster; permissão de deploy separada de permissão de leitura. Leia `references/secrets-and-identity.md`.
   5.5 **Deploy progressivo**: rolling com `maxUnavailable`/`maxSurge` conscientes, blue-green para troca atômica, canary com limite de erro e análise. Readiness antes de receber tráfego; liveness sem derrubar por dependência lenta; `PodDisruptionBudget` e resource requests/limits definidos. Leia `references/deploy-strategies.md`.
   5.6 **Rollback e recuperação**: toda release tem volta — imagem anterior por digest, migração compatível com N-1, feature flag para desligar caminho novo, backup verificado antes de mudança destrutiva. Rollback automático por métrica e rollback manual com runbook. Leia `references/rollback-and-recovery.md`.

## Padrões inegociáveis
- **Imagem por digest** em produção; tags mutáveis proibidas no caminho de deploy.
- **Nenhum segredo** em imagem, repositório, log, `ARG` de Dockerfile ou variável pública de CI.
- **Mesmo artefato** do gate até produção — rebuild por ambiente é proibido.
- **Gate que bloqueia**: teste, scan de imagem, scan de dependência e política falham → pipeline para.
- **Readiness/liveness** e resource limits obrigatórios em todo workload.
- **Migração compatível com N-1**; expand/contract; nunca `DROP` sem backup verificado e autorização.
- **Rollback ensaiado** em staging antes de produção; RTO/RPO declarados.
- **Produção com autorização explícita** e janela; nada de deploy manual silencioso.
- **Observabilidade do release**: métrica de erro/latência, log com versão e alerta no caminho novo.
- **Custo e capacidade**: requests realistas, HPA com métrica correta, sem overprovisionar por medo.
- **Supply chain**: SBOM, assinatura e scan de vulnerabilidade; imagem com CVE crítica não publica.
- **Ação destrutiva** (delete namespace, force push, rotate secret, drop) exige plano de volta e confirmação.

## Estratégias de deploy
| Estratégia | Quando usar | Rollback |
|---|---|---|
| Rolling update | padrão; stateless, zero-downtime gradual | `kubectl rollout undo` |
| Blue-green | alta criticidade; troca atômica de tráfego | trocar seletor do Service |
| Canary | validar em fração (10 → 50 → 100%) com métrica por versão | retirar peso / escalar réplicas |
| Recreate | stateful com schema break; exige janela | manual e planejado |

Critério de sucesso e gatilho de aborto definidos **antes** do deploy. Deploy ≠ release: feature flag
desacopla.

## Gestão de segredos
1. Nunca em código, `Dockerfile` (`ARG`/`ENV`), manifesto em texto puro, log, artifact ou vault.
2. Sempre em: Sealed Secrets (`kubeseal`), External Secrets Operator (AWS SM / GCP SM / Azure KV),
   Vault/OpenBao, Docker Secret.
3. `.env` só em local/staging, fora do Git, com scan no diff.
4. Rotação documentada (quem, quando, como o app recarrega) e acesso auditado.

```yaml
# Sealed Secret (cifrado, seguro no Git)
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata: {name: app-secrets, namespace: production}
spec:
  encryptedData:
    DATABASE_URL: AgBy3i4OJSWK+PiTySYZZA9rO43cGDEq...
```
```bash
kubectl create secret generic app-secrets --from-env-file=.env.prod \
  --dry-run=client -o yaml | kubeseal --format yaml > infra/sealed-secret.yaml
```

## Vereditos
| Veredito | Critério |
|---|---|
| `PASS` | todas as etapas do escopo com evidência e health/smoke verdes |
| `PARTIAL` | subset passou; restante com motivo declarado |
| `FAIL` | etapa crítica falhou; rollback executado (se produção) |
| `BLOCKED` | pré-condição não atendida; nenhuma ação destrutiva tomada |

Matriz de evidência por etapa em `templates/deployment-report.md`. Sem arquivo de evidência, o estado é
`NOT_TESTED` — não `PASS`.

## Quality gates
Leia `references/quality-gates.md`. Resumo — BLOCKER: segredo no artefato, imagem sem digest em prod, deploy sem health check, gate desabilitado para passar, rollback inexistente, `DROP`/delete sem backup, permissão de admin no CI, imagem com CVE crítica publicada. MAJOR: ausência de probe, sem resource limits, rebuild por ambiente, rollback não ensaiado, sem alerta no caminho novo, `latest` em staging.

## Checklist de encerramento
- [ ] Scan de secrets: 0 findings
- [ ] `.dockerignore` existe e cobre `node_modules/`, `.git/`, `.env*`, `dist/`, `coverage/`, `*.log`
- [ ] SAST: sem `ERROR` (ou `NOT_TESTED` declarado se semgrep ausente)
- [ ] Scan de imagem: sem `CRITICAL/HIGH`
- [ ] Push com digest SHA-256 registrado
- [ ] `terraform plan` revisado + aplicado (ou `NOT_TESTED` declarado)
- [ ] Rollout completou sem erro
- [ ] `/healthz` responde 200 e `/readyz` responde ready (com DB/cache)
- [ ] Smoke E2E verde
- [ ] Log rotation configurada (`max-size=10m`, `max-file=5`)
- [ ] Backup recente + **restore ensaiado**
- [ ] `estado.md` atualizado com veredito, imagem e comando de rollback
- [ ] Nenhum segredo em log, artifact, vault ou chat

## Seleção de referências (carregamento progressivo)
- Imagem, Dockerfile e tamanho: `references/container-images.md`
- Auditoria de infraestrutura, blast radius e threat model: `references/infrastructure-audit.md`
- Compose, redes e o bypass de UFW: `references/compose-and-networking.md`
- Proxy reverso, TLS e headers: `references/edge-proxy-tls.md`
- Pipeline, cache e artefato imutável: `references/build-and-artifacts.md`
- Config, ambientes e validação: `references/environments-and-config.md`
- Segredos, OIDC, Sealed Secrets e menor privilégio: `references/secrets-and-identity.md`
- Kubernetes, probes, recursos e HPA: `references/kubernetes-and-orchestration.md`
- Estratégias de deploy: `references/deploy-strategies.md`
- Migração zero-downtime: `references/migrations-safe.md`
- Rollback, backup e continuidade: `references/rollback-and-recovery.md`
- SLO, métricas, backup 3-2-1 e DR: `references/observability-backup-dr.md`
- SLO, orçamento de erro, painel mínimo, trace e smoke pós-deploy: `references/observability-and-slo.md`
- Supply chain (SBOM, assinatura, scan): `references/supply-chain-security.md`
- Gates e severidade: `references/quality-gates.md`
- Anti-padrões com correção: `references/anti-patterns.md`
- Templates: `templates/Dockerfile`, `templates/compose.template.yml`, `templates/k8s-deployment.yaml`,
  `templates/ci-pipeline.yml`, `templates/deployment-report.md`, `templates/rollback-plan.md`,
  `templates/deploy-runbook.md`
- Scripts: `scripts/preflight.sh` (CLIs disponíveis), `scripts/release_probe.py` (sonda de health/readiness)
- Instalação: `references/installation.md`

## Roteamento com outras skills
| Situação | Skill |
|---|---|
| Schema, migração, contrato de API | `dz23-backend-data-architect` |
| Validar fluxo no browser após deploy | `dz23-e2e-browser-verifier` |
| Revisão de segurança antes de expor | `security-review` |
| Proteção de dados e segredos em pipeline | `security-review` / `delivery-pipeline` |
| Ciclo autônomo de `/goal` | `dz23-autonomous-improvement-ultimate` |
| UI e regressão visual | `dz23-ultimate-pro-max` |

Regra: **não crie um segundo orquestrador**. Esta skill entrega o deploy; ela não substitui `/goal`.

## Contrato de resposta
Para tarefa executável: diagnóstico, artefato gerado (imagem com digest), pipeline/gates, ambiente, comandos e saída, métricas do release, rollback disponível, riscos e o que **não** foi testado. Execute autonomamente mudanças reversíveis em ambiente de desenvolvimento; peça autorização para produção, mudança destrutiva, rotação de segredo e aumento de permissão.

## Gatilho de ativação
"Use a skill dz23-devops-cloud-deployer, leia SKILL.md e as referências pertinentes, audite a stack, produza imagem mínima e reproduzível, monte o pipeline com gate que bloqueia, publique de forma progressiva com health check e me entregue o rollback ensaiado. Não aceite segredo no artefato, imagem sem digest, gate desabilitado nem deploy sem volta."
