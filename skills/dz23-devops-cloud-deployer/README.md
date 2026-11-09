# DZ23 DevOps Cloud Deployer v1.0.0

Skill de DevSecOps, containers e deploy autônomo com evidência para DeepSeek Harness e agentes compatíveis com `SKILL.md`.

Cobre o caminho completo: **auditar a stack → planejar → construir imagem reproduzível → pipeline com gate → publicar progressivo → observar → reverter se preciso → entregar**.

## Conteúdo

| Arquivo | Para quê |
|---|---|
| `SKILL.md` | Missão, workflow em 9 etapas e módulos 5.1–5.6 |
| `references/container-images.md` | Multi-stage, base por digest, non-root, reprodutibilidade |
| `references/infrastructure-audit.md` | Inventário, blast radius e threat model |
| `references/compose-and-networking.md` | `edge_net`/`internal_net`, bind seguro, bypass de UFW, limites |
| `references/edge-proxy-tls.md` | Caddy/Traefik, TLS automático, headers e rate limit |
| `references/build-and-artifacts.md` | Um build por commit, promoção por digest, gates |
| `references/environments-and-config.md` | 12-factor, validação de config, paridade |
| `references/secrets-and-identity.md` | Sealed Secrets, ESO, OIDC, menor privilégio |
| `references/kubernetes-and-orchestration.md` | Probes, requests/limits, PDB, HPA, GitOps |
| `references/deploy-strategies.md` | Rolling, blue-green, canary, feature flag |
| `references/migrations-safe.md` | Expand/contract e forward-fix no deploy |
| `references/rollback-and-recovery.md` | Três formas de voltar, backup verificado |
| `references/observability-backup-dr.md` | `/healthz` × `/readyz`, log rotation, backup 3-2-1, DR |
| `references/observability-and-slo.md` | SLO, orçamento de erro, painel mínimo, trace, smoke pós-deploy |
| `references/supply-chain-security.md` | SBOM, scan, assinatura, rebuild de base |
| `references/quality-gates.md` | Gates e severidade (BLOCKER/MAJOR/MINOR) |
| `references/anti-patterns.md` | 48 erros recorrentes com sintoma, dano e correção |
| `references/installation.md` | Instalação e ferramentas esperadas |
| `templates/Dockerfile` | Multi-stage, non-root, base pinada por digest |
| `templates/compose.template.yml` | Compose segmentado com hardening e limites |
| `templates/k8s-deployment.yaml` | Probes, limits, securityContext, PDB, HPA |
| `templates/ci-pipeline.yml` | Build único, scan bloqueante, SBOM, promoção por digest |
| `templates/deployment-report.md` | Matriz de evidência por etapa + veredito |
| `templates/rollback-plan.md` | Plano de rollback preenchido antes do deploy |
| `templates/deploy-runbook.md` | Runbook com critério de sucesso, aborto e rollback |
| `scripts/preflight.sh` | Reporta CLIs disponíveis (não instala nada) |
| `scripts/release_probe.py` | Sonda `/healthz` + readiness + revision (reimplementação mínima) |
| `scripts/validate_skill.py` | Validador documental |

## Escopo

Instruções e metodologia. Não provisiona infraestrutura nem executa deploy por conta própria: exige
autorização para produção e declara o que não foi testado. A skill exige evidência — digest, log do
pipeline, health check, métrica e rollback ensaiado.

## Uso

1. Instalar no diretório de skills (`references/installation.md`).
2. Invocar por `/dz23-devops-cloud-deployer` ou por descrição ("monte o pipeline com gate e o rollback ensaiado").
3. Combinar com `dz23-backend-data-architect` (migração), `dz23-e2e-browser-verifier` (smoke pós-deploy),
   `security-review` e `delivery-pipeline`.

**Prompt de ativação:** [`PROMPT-ATIVACAO.txt`](PROMPT-ATIVACAO.txt).

**Avaliação:** `evals/evals.json` — 15 cenários (schema 1). Cenários não são testes executados: rode em
harness real e registre o resultado por caso.

**Versão:** [`VERSION`](VERSION) (1.0.0) · histórico em [`CHANGELOG.md`](CHANGELOG.md).

## Princípio

Deploy que não tem volta não é entrega, é aposta. `NOT_TESTED` nunca vira `PASS`.

---

## Arsenal — resumo operacional

**Versão real (VERSION/frontmatter):** 1.2.1 · **Categoria:** devops · **Complexidade:** advanced

### Quando usar

- Containerizar aplicação (imagem mínima, reproduzível, sem root).
- Montar ou corrigir pipeline de CI/CD com gates.
- Provisionar ambiente e preparar rollback ensaiado.
- DevSecOps: scan de imagem, dependência e segredo.

### Quando NÃO usar

- Deploy em produção sem autorização explícita — a skill exige, não assume.
- Projeto que não tem deploy (biblioteca local).
- Otimização de latência (use `dz23-performance-scalability-engine`).

### Instalação

```bash
# Já incluída no install-all. Manual:
cp -r skills/dz23-devops-cloud-deployer ~/.agents/skills/dz23-devops-cloud-deployer
```

### Uso

```bash
/dz23-devops-cloud-deployer

# ou por descrição — o agente carrega sozinho (ver SKILL.md)
```

### Pré-requisitos de CLI

`docker`, `git`, `trivy` (obrigatórias) · `kubectl`, `helm`, `terraform`, `hadolint`, `gitleaks` (recomendadas — sem elas, parte do fluxo fica `BLOCKED`).

### Evidência / Quality gates

- Build reprodutível: pin por digest, sem `latest`.
- Gate de scan sem CRITICAL/HIGH aberto.
- Rollback ensaiado, não prometido.
- Observabilidade mínima: SLO, painel, trace, smoke pós-deploy.

### Integração com outras skills

Recebe imagem/pipeline de `dz23-backend-data-architect`; entrega ambiente para `dz23-e2e-browser-verifier`; recebe gargalo de infra de `dz23-performance-scalability-engine`.

### Versão e changelog

Ver [`CHANGELOG.md`](CHANGELOG.md) (desta skill) e o histórico do arsenal em [`../../CHANGELOG.md`](../../CHANGELOG.md).
