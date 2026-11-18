# Modo offline — dz23-arsenal

O que funciona sem rede, e o que honestamente **não** funciona.

## Funciona offline (sem nenhuma rede)

- **Instalação:** `scripts/dz23-install.py` é cópia de arquivos pura — zero rede (garantido pelo
  `install:autoteste`). O caminho `install-all.sh/.ps1` também.
- **Quality gate:** `scripts/quality-gate.py` roda os 109 checks offline — validação de skills,
  evals, estrutura, links, números, licenças, segredos, catálogo, SBOM, permissões, instalador,
  replay. Nada chama a rede.
- **Scripts do arsenal:** Python stdlib puro; nenhuma dependência de runtime a baixar.
- **MCP `dz23-subagents-universal-mcp`:** zero dependências de terceiros (roda sem `npm install`).
- **Consultas internas (acervos):** `consulta-*.py` leem dados locais; `web-design-guidelines`,
  `dados-design`, backend/postgres/devops/e2e/reverse são consultáveis offline.
- **Replay de eval:** `replay-eval.py` re-gradua respostas registradas, sem rede.

## Exige rede (declara `BLOCKED` offline)

- **MCP `pentagi-mcp`:** `npm install` das 3 deps diretas (`@modelcontextprotocol/sdk`, `undici`,
  `zod`); e o serviço PentAGI self-hosted.
- **Skills de deploy/cloud** (`dz23-devops-cloud-deployer`): registry, cloud, provedores.
- **Skills de rede/scraping** (`replica-recon`, `replica-brand`): coleta na web.
- **E2E/browser** (`dz23-e2e-browser-verifier`): download do browser e o alvo.
- **Integrações externas catalogadas** (Ollama, LiteLLM, OpenHands, …): baixam/conectam.
- **CI (Gitleaks/CodeQL/Dependabot):** rodam no GitHub, não offline.

## Regra

Sem rede, uma skill que precisa de rede **não** finge sucesso: declara
`BLOCKED_BY_EXTERNAL_DEPENDENCY` e segue o que dá para fazer offline (desenho, contrato, validação
de payload). Ver [`LIMITATIONS.md`](LIMITATIONS.md).
