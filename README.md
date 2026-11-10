# dz23-arsenal

Coleção de 9 skills, 1 MCP e 1 bundle de engenharia para agentes de IA (Claude Code, DeepSeek Harness,
Cursor, Codex). Cada item é uma capacidade completa — não um prompt solto.

![Skills](https://img.shields.io/badge/skills-9-blue)
![MCP](https://img.shields.io/badge/mcp-1-green)
![Bundle](https://img.shields.io/badge/bundle-1-purple)
![License](https://img.shields.io/badge/license-MIT-yellow)

## O que é isto

Este repositório é um **arsenal de skills** para agentes de engenharia de software. Cada skill é
auto-contida: `SKILL.md` (as regras), `references/` (conhecimento carregado sob demanda), `templates/`
(artefatos preenchíveis), `scripts/` (código executável, quando existe) e `evals/` (cenários de
avaliação).

A ideia central é **evidência ou silêncio**: cada skill define o que conta como prova, o que é
`NOT_TESTED` e o que bloqueia a entrega. Não há "parece que funciona".

## Quick start (30 segundos)

```bash
# Clone
git clone https://github.com/LMPrado-DZ23/dz23-arsenal.git
cd dz23-arsenal

# Instale todas as skills (Windows)
.\scripts\install-all.ps1

# Ou Linux/Mac
./scripts/install-all.sh

# Verifique o que foi instalado e quais CLIs faltam
python scripts/audit-zips.py
pwsh scripts/verify-cli.ps1
```

As skills ficam em `~/.agents/skills/<nome>/` e são descobertas automaticamente por Claude Code, DeepSeek
Harness, Codex e Cursor (via junction/symlink de `~/.claude/skills` e `~/.codex/skills`).

## Índice — Skills DZ23 (10)

| Skill | Versão | Para quê | Quando usar |
|---|---|---|---|
| [`dz23-autonomous-improvement-ultimate`](skills/dz23-autonomous-improvement-ultimate/) | 2.1 | Loop de correção com evidência | Qualquer `/goal` de melhoria |
| [`dz23-backend-data-architect`](skills/dz23-backend-data-architect/) | 1.1.0 | Backend, DB, contratos | API, schema, migration |
| [`dz23-codebase-cartographer`](skills/dz23-codebase-cartographer/) | 1.1.0 | Mapeamento de codebase | Onboarding, antes de refactor |
| [`dz23-devops-cloud-deployer`](skills/dz23-devops-cloud-deployer/) | 1.2.1 | Deploy, CI/CD, IaC | Container, K8s, cloud |
| [`dz23-e2e-browser-verifier`](skills/dz23-e2e-browser-verifier/) | 1.1.0 | E2E com Playwright | Verificação de UI |
| [`dz23-performance-scalability-engine`](skills/dz23-performance-scalability-engine/) | 1.3.0 | Otimização 4 camadas | Performance, latência, budget |
| [`dz23-postgres-prod-preflight`](skills/dz23-postgres-prod-preflight/) | 1.0.0 | Pré-deploy de banco: 10 gates | Antes de subir schema, RLS ou credencial |
| [`dz23-reverse-engineer-anything`](skills/dz23-reverse-engineer-anything/) | 1.1.1 | RE de binários/firmware | Análise de binário, CTF, audit |
| [`dz23-spec-to-system-engine`](skills/dz23-spec-to-system-engine/) | 1.2.0 | Spec executável | PRD, decomposição, Gherkin |
| [`dz23-ultimate-pro-max`](skills/dz23-ultimate-pro-max/) | 2.2.0 | Frontend/UI/UX | Componente, landing, a11y |

Índice detalhado com tabela comparativa: [`skills/README.md`](skills/README.md).

## Índice — MCP e Bundle

| Item | Tipo | Versão | Para quê |
|---|---|---|---|
| [`dz23-subagents-universal-mcp`](mcp/dz23-subagents-universal-mcp/) | MCP (Node) | 4.4.1 | Sub-agentes com 28 tools |
| [`dz23-dsh-agency`](bundle/dz23-dsh-agency/) | Bundle | 1.0.0 | 88 agentes especializados + Diretor |

## Skills externas recomendadas (9)

| Skill | Autor | Para quê | Repo |
|---|---|---|---|
| [Superpowers](external/superpowers.md) | obra | Planejamento + disciplina (SDLC) | [link](https://github.com/obra/superpowers) |
| [UI UX Pro Max](external/ui-ux-pro-max.md) | nextlevelbuilder | Design intelligence por segmento e stack | [link](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) |
| [REA](external/rea.md) | morluto | Engenharia reversa + binários | [link](https://github.com/morluto/rea) |
| [Cloudflare Security Audit](external/cloudflare-security-audit.md) | cloudflare | Auditoria de segurança de source | [link](https://github.com/cloudflare/security-audit-skill) |
| [Anthropic Skills](external/anthropic-skills.md) | anthropic | skill-creator, mcp-builder, pdf, docx, xlsx, pptx | [link](https://github.com/anthropics/skills) |
| [Vercel React Best Practices](external/vercel-react-best-practices.md) | vercel-labs | Performance React/Next | [link](https://github.com/vercel-labs/agent-skills) |
| [Supabase Postgres Best Practices](external/supabase-postgres-best-practices.md) | supabase | Postgres/Supabase | [link](https://github.com/supabase/agent-skills) |
| [Playwright MCP](external/playwright-mcp.md) | microsoft | Testes E2E via MCP | [link](https://github.com/microsoft/playwright-mcp) |
| [Terraform AWS VPC](external/terraform-aws-vpc.md) | terraform-aws-modules | VPC AWS IaC | [link](https://github.com/terraform-aws-modules/terraform-aws-vpc) |

Cada linha linka para `external/<nome>.md` com instruções completas de instalação e uso.

## Prompts de origem

Os prompts que deram origem a algumas skills. Servem para **uso direto** (copiar e colar, sem instalar
nada) e para **rastreabilidade** (de onde veio cada skill).

| Prompt | O que pede | Virou a skill |
|---|---|---|
| [`prompts/performance-4-camadas.md`](prompts/performance-4-camadas.md) | plano de otimização em 4 camadas, 20 itens | [`dz23-performance-scalability-engine`](skills/dz23-performance-scalability-engine/) |

Índice e comparação prompt × skill: [`prompts/README.md`](prompts/README.md).

## Pré-requisitos de CLI

- **Base para todas as skills**: `git`, `python` (3.10+), `node` (20+), `rg`, `jq`, `curl`
- **Por skill**: ver [`cli/required.md`](cli/required.md) — cada skill tem dependências próprias
  (`docker`/`kubectl`/`trivy` para devops, `playwright` para e2e, etc.)
- **O que falta nesta máquina**: ver [`cli/recommended.md`](cli/recommended.md) — inventário real,
  com prioridade ALTA/MÉDIA/BAIXA
- **Instalação**: [`cli/install-windows.md`](cli/install-windows.md) ou
  [`cli/install-linux.md`](cli/install-linux.md)
- **Verificação**: `pwsh scripts/verify-cli.ps1`

## Integração entre skills

```mermaid
graph TD
    A[spec-to-system-engine] --> B[backend-data-architect]
    A --> C[ultimate-pro-max]
    B --> D[devops-cloud-deployer]
    C --> E[e2e-browser-verifier]
    D --> E
    F[codebase-cartographer] --> B
    F --> C
    G[performance-scalability-engine] --> B
    G --> C
    H[autonomous-improvement-ultimate] -.orquestra.-> A
    H -.orquestra.-> B
    H -.orquestra.-> C
    I[reverse-engineer-anything] --> F
```

Mapa detalhado (quem chama quem, e por quê): [`docs/integration-map.md`](docs/integration-map.md).

## Documentação

| Documento | Para quê |
|---|---|
| [`docs/getting-started.md`](docs/getting-started.md) | Do zero ao primeiro uso |
| [`docs/skills-overview.md`](docs/skills-overview.md) | Tabela comparativa das 9 skills |
| [`docs/integration-map.md`](docs/integration-map.md) | Como as skills se conectam |
| [`docs/installing-skills.md`](docs/installing-skills.md) | DZ23 → `~/.agents/skills` |
| [`docs/faq.md`](docs/faq.md) | Perguntas frequentes |
| [`cli/README.md`](cli/README.md) | Guia de CLIs |

## Estado verificado (não é marketing)

Este repo publica **10 skills DZ23 + 1 MCP + 1 bundle + 7 skills externas empacotadas** e **9 referências
externas** documentadas. **O que está publicado é diferente do que está verificado.**

| Métrica | Valor |
|---|---|
| Skills publicadas | **10** DZ23 + 1 MCP + 1 bundle + 7 externas (+9 referências externas) |
| Evals declarados | **144** |
| **Evals executados** | **45/144 (31,2%)** — 43 PASS · 2 PARTIAL · 0 FAIL |
| **Evals auditados em literais** | **16/16 da amostra** (re-auditorias de 2026-11-09) |
| **Laudo original da auditoria** | **`INVALIDO_COMO_EVIDENCIA`** — 54 de 68 citações não existem nas respostas |
| Críticos executados | **32 de 45 identificados (71%)** — 13 exigem infra |
| Camada 4 (projeto real) | **1 tarefa** no próprio repo — CI verde após **5 iterações** de correção |
| CI | ✅ verde · **16/16** no gate |
| Release | **v1.4.9** com 18 assets |

### 5 camadas de verificação

Cada camada conserta a anterior e cria um erro próprio, de natureza nova. O repo mede as cinco porque
nenhuma enxerga o que a outra enxerga:

| Camada | Cobertura | Erro que só ela mostra |
|---|---|---|
| 1 — autoavaliação | 45/144 | viés de confirmação |
| 2 — re-leitura adversarial | 20/45 | violação de regra **vizinha** ao eval |
| 3 — auditoria externa | 16/16 da amostra, em literais | paráfrase do input + citação fabricada |
| 4 — projeto real | 1 tarefa (CI verde) | ferramenta acusando evidência **legítima** |
| 5 — conferência mecânica | 2 scripts dentro do gate | amostragem preguiçosa da própria conferência |

**Nenhuma camada substitui a próxima.** A 4 é a única que ainda não errou — porque uso em projeto de outra
pessoa transforma erro em retrabalho, não em parágrafo.

### O que NÃO está provado

- **99 de 144 evals nunca executados** (68,8%)
- **40 evals bloqueados** por ausência de infra (Docker/Postgres/Ghidra/browser/hardware), 13 deles críticos
- **3 evals criados na v1.4.5** (OB-03/04/05) nunca executados nem auditados
- **Camada 4 fora do próprio repo:** 0 tarefas
- **Uso em produto de outra pessoa:** 0

O repo é honesto sobre o que afirma. Não é cobertura completa, e não tem 100% de nada.

Detalhes da Camada 4: [`docs/camada-4-2026-11-09.md`](docs/camada-4-2026-11-09.md) · método:
[`docs/eval-methodology.md`](docs/eval-methodology.md) · estado por eval:
`python scripts/run-evals.py --audit`

Verificar agora:

```bash
python scripts/quality-gate.py              # 16 checks
python scripts/run-evals.py --report        # 45/131
python scripts/run-evals.py --verify-quotes # citações dos laudos válidos
```

Detalhe por skill: [`ROADMAP.md`](ROADMAP.md#status-de-evals-atualizado-2026-11-09) · registros:
[`evals-results/`](evals-results/).

## Qualidade — um comando, um veredito

```bash
python scripts/quality-gate.py
```

Roda: validador de cada skill · estrutura (arquivos obrigatórios, frontmatter, `VERSION` × frontmatter,
schema dos evals) · links relativos · manifesto atualizado. Exit `0` só se **tudo** passar. O mesmo gate
roda em CI a cada push ([`.github/workflows/quality.yml`](.github/workflows/quality.yml)).

| Ferramenta | Para quê |
|---|---|
| [`scripts/quality-gate.py`](scripts/quality-gate.py) | roda todos os checks e dá o veredito |
| [`scripts/check-structure.py`](scripts/check-structure.py) | arquivos obrigatórios, frontmatter, `VERSION`, schema de evals |
| [`scripts/check-links.py`](scripts/check-links.py) | todo link relativo `.md` |
| [`scripts/build-manifest.py`](scripts/build-manifest.py) | gera [`arsenal.json`](arsenal.json) e [`INDEX.md`](INDEX.md) |
| [`scripts/audit-zips.py`](scripts/audit-zips.py) | compara o repo com as skills instaladas |
| [`scripts/verify-cli.ps1`](scripts/verify-cli.ps1) | inventário real de CLIs da máquina |

## Documentos do repositório

| Documento | Conteúdo |
|---|---|
| [`INDEX.md`](INDEX.md) | inventário gerado (versão, arquivos, refs, evals por skill) |
| [`ROADMAP.md`](ROADMAP.md) | estado honesto: o que foi verificado e o que é `NOT_TESTED` |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | como propor mudança |
| [`SECURITY.md`](SECURITY.md) | como reportar vulnerabilidade |
| [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) | regra de convivência |
| [`CHANGELOG.md`](CHANGELOG.md) | histórico do arsenal |

## Como contribuir

Leia [`CONTRIBUTING.md`](CONTRIBUTING.md). Contribuição é bem-vinda em: correção de fato técnico,
novo eval que exponha uma falha real, e nova referência externa.

## Licença

MIT — ver [`LICENSE`](LICENSE).

## Créditos

As 9 skills DZ23 foram construídas ao longo de sessões de desenvolvimento iterativo, com auditoria por
três modelos diferentes (Claude, Gemini, ChatGPT) e verificação empírica contra o ambiente real. As
referências externas pertencem aos seus respectivos autores e mantêm suas licenças.

## Aviso honesto sobre evals

As 9 skills declaram **~137 cenários** em `evals/evals.json`. Executados em harness real e julgados:
**3** — mais 1 (`pass-sem-teste`) na skill de orquestração. O resto é `NOT_TESTED`, declarado no
`CHANGELOG.md` de cada skill e no [`ROADMAP.md`](ROADMAP.md).

Skill com eval não executado é skill com comportamento **não comprovado**. Trate `evals/evals.json` como
especificação de comportamento, não como certificado.

O próximo passo para fechar esse buraco está descrito no `ROADMAP.md` (dívida #1): um harness
`scripts/run-evals.py` que executa, registra veredito e guarda evidência. Enquanto ele não existir, o
número honesto continua sendo **3 de 137**.
