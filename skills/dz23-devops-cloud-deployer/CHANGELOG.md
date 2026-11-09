# Changelog — dz23-devops-cloud-deployer

## [1.2.2] — 2026-11-09

### Adicionado
- Seção **Backup e DR com RTO/RPO numéricos**: alvo obrigatório (`RTO < 15 min`, `RPO < 5 min`), "medir" é
  etapa e não resposta, e default explícito quando o dono não declarou. Fecha OB-04 da auditoria externa de
  2026-11-09.
- Novo eval `rto-rpo-without-numeric-target` (16 casos).

## [1.2.1] — 2026-11-08

Fix de empacotamento, não de conteúdo. Nenhuma reference foi alterada.

### Corrigido
- **O zip da v1.2.0 foi empacotado sem 2 linhas** — a citação de `references/observability-and-slo.md`
  em `SKILL.md` (seção de seleção de referências) e em `README.md` (tabela de arquivos). A skill
  **instalada** já estava correta desde a v1.2.0; o artefato publicado é que ficou atrás.
- **v1.2.1 inclui a correção** e é o primeiro zip gerado a partir do estado instalado verificado
  arquivo por arquivo (0 divergências).
- Zip v1.2.0 preservado em `_antigos/` como referência (`52.598 B`, o conteúdo velho).

### Disciplina de release
- Corrigir conteúdo sem bump foi o erro da rodada anterior (zip v1.2.0 reempacotado com o mesmo número e
  hash diferente, `52.673 B`). Esta versão existe para que o número reflita o conteúdo — mesma lição da
  auditoria: **um artefato com o mesmo nome e conteúdo diferente é ambíguo por definição.**

## [1.2.0] — 2026-11-08

Fix dos 4 gaps encontrados pelos evals em Docker real.

### Corrigido
- SKILL.md: header `v1.0` → `v1.1` (cosmético, alinha frontmatter) e, no fechamento, → `v1.2`
- `references/supply-chain-security.md`: fallback `trivy fs` ganhou comando executável + critério de
  saída (antes era decorativo)
- `references/container-images.md`: pin por digest explícito para `FROM` base (antes só para imagem final)
- SKILL.md checklist: `.dockerignore` como item objetivo

### Evidência
- 3 evals em Docker real: `secret-in-image` PASS 5/5, `latest-tag-in-prod` PASS 5/5,
  `no-health-after-deploy` PASS 5/5
- `resultado.md` em `projects/devops-eval-test/`

## [1.1.0] — 2026-11-08

Merge com 3 propostas externas (Claude, Gemini, ChatGPT) + relatório Manus. Preserva os 12 references,
4 templates, quality-gates, 36 anti-padrões, evals e o validador existentes.

### Adicionado
- 5 references novos: `infrastructure-audit`, `compose-and-networking` (bypass de UFW via iptables,
  `edge_net`/`internal_net`), `edge-proxy-tls` (Caddy/Traefik, TLS, headers), `migrations-safe`
  (expand/contract), `observability-backup-dr` (backup 3-2-1, restore ensaiado, RTO/RPO)
- 3 templates novos: `compose.template.yml`, `deployment-report.md`, `rollback-plan.md`
- 2 scripts novos: `preflight.sh` (CLIs disponíveis) e `release_probe.py` (reimplementação mínima
  documentada — o helper original do Manus não é recuperável)
- SKILL.md: seções Pré-condições (CLIs reais desta máquina), Pipeline em 4 fases, Estratégias de deploy,
  Gestão de segredos (Sealed Secrets/ESO), Vereditos e Checklist de encerramento
- `secrets-and-identity.md`: Sealed Secrets, External Secrets Operator, rotação e auditoria de acesso
- 12 anti-padrões novos (36 → 48), incluindo UFW bypass, `npm start` como PID 1, log sem rotação e
  `ARG` de build com segredo

### Corrigido
- Referência de skill de UI normalizada para `dz23-ultimate-pro-max`

### Nota
- helm/terraform/podman/gitleaks/semgrep ausentes nesta máquina: a skill declara
  `BLOCKED_BY_EXTERNAL_DEPENDENCY` e oferece alternativas (`kubectl` direto, `trivy fs` como substituto
  de gitleaks, SAST como `NOT_TESTED`)

## [1.0.0] — 2026-11-08

Primeira versão.

- `SKILL.md`: missão, precedência, workflow em 9 etapas e módulos 5.1–5.6 (imagem, build/artefato,
  config/ambientes, segredos/identidade, deploy progressivo, rollback/recuperação).
- 12 references: containers, build e artefato, config por ambiente, segredos e OIDC, Kubernetes,
  estratégias de deploy, rollback e continuidade, observabilidade e SLO, supply chain, quality gates,
  anti-padrões (36) e instalação.
- 4 templates: `Dockerfile` (multi-stage, non-root, base por digest), `k8s-deployment.yaml`
  (probes, limits, securityContext, PDB, HPA), `ci-pipeline.yml` (build único, scan bloqueante, SBOM,
  promoção por digest) e `deploy-runbook.md`.
- 15 cenários de avaliação em `evals/evals.json` (schema 1).
- Padrões inegociáveis: imagem por digest, zero segredo no artefato, um build por commit,
  gate que bloqueia, probes e limits obrigatórios, migração compatível com N-1, rollback ensaiado,
  produção com autorização e observabilidade do release.
