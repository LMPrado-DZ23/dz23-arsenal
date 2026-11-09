# Instalação

## DeepSeek Harness (DSH)
1. Copie a pasta `dz23-devops-cloud-deployer/` para `C:\Users\<usuário>\.agents\skills\`.
2. Descoberta lê `SKILL.md` na raiz — não precisa reiniciar.
3. Invoque por `/dz23-devops-cloud-deployer` ou por descrição ("monte o pipeline com gate e o rollback ensaiado").
4. `~/.claude/skills` e `~/.codex/skills` apontam para `~/.agents/skills` (junction): instalar uma vez alcança os três.

## Ferramentas esperadas (opcionais por stack)
| Uso | Ferramenta |
|---|---|
| Container | docker/podman |
| Orquestração | kubectl, helm |
| GitOps | argocd/flux (opcional) |
| Scan | trivy, grype, gitleaks |
| SBOM/assinatura | syft, cosign |
| IaC | terraform, opentofu |

A skill é instrução: não instala nada por conta própria. Ferramenta só conta quando exercitada.

## Variáveis que a skill espera encontrar no projeto
```bash
GIT_SHA=...            # injetado no build
REGISTRY=...           # registry privado
IMAGE_DIGEST=...       # preenchido após push
SLO_ERROR_RATE=0.01    # limite de erro aceitável no deploy
```
Nunca commitar valores de segredo.

## Estrutura
```
dz23-devops-cloud-deployer/
  SKILL.md
  README.md
  CHANGELOG.md
  VERSION
  PROMPT-ATIVACAO.txt
  references/ (12 arquivos)
  templates/
    Dockerfile
    k8s-deployment.yaml
    ci-pipeline.yml
    deploy-runbook.md
  scripts/validate_skill.py
  evals/evals.json
```

## Verificação
```bash
python scripts/validate_skill.py
```

## Uso combinado
- `dz23-backend-data-architect` — migração e contrato antes do deploy.
- `dz23-e2e-browser-verifier` — smoke e validação de fluxo após publicar.
- `security-review` — revisão antes de expor.
- `delivery-pipeline` — quando o foco é só o pipeline.
- `dz23-autonomous-improvement-ultimate` — deploy dentro de `/goal`.
