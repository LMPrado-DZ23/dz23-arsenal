# Changelog — dz23-arsenal

Histórico de releases **do arsenal**. O changelog de cada skill fica dentro da própria pasta
(`skills/<nome>/CHANGELOG.md`).

## [1.3.0] — 2026-11-09

Transformação de "coleção de zips" em **arsenal verificável**: gate único, CI, inventário gerado e política
de contribuição/segurança.

### Adicionado
- **`scripts/quality-gate.py`** — roda tudo (validador de cada skill, estrutura, links, manifesto) e dá um
  veredito com exit code. Um comando, um veredito.
- **`scripts/check-structure.py`** — arquivos obrigatórios por skill, frontmatter (`name`/`version`/
  `description`/`user-invocable`), `name` == pasta, `VERSION` == frontmatter, `CHANGELOG` com a versão atual,
  README com seção Arsenal, schema dos evals, detecção de skill-esqueleto.
- **`scripts/check-links.py`** — valida todo link relativo `.md` do repositório (133 links).
- **`scripts/build-manifest.py`** + **`arsenal.json`** + **`INDEX.md`** — inventário legível por máquina e
  índice gerado dos próprios arquivos; `--check` falha se estiver desatualizado.
- **CI** em [`.github/workflows/quality.yml`](.github/workflows/quality.yml) — roda o gate em push/PR e
  publica `gate.json` como artefato.
- **`SECURITY.md`** — canal privado, o que conta como vulnerabilidade neste projeto, prazo de melhor esforço.
- **`CODE_OF_CONDUCT.md`** — regra de convivência curta, centrada em evidência.
- **`ROADMAP.md`** — estado honesto: o que foi verificado, as 7 dívidas conhecidas e os não-objetivos.
- **`.github/ISSUE_TEMPLATE/{bug,feature}.md`** e **`pull_request_template.md`** — formulários que exigem
  evidência literal.
- **`.gitattributes`** — normaliza LF no repositório (CRLF só em `.ps1`/`.cmd`), evitando churn de fim de linha.

### Corrigido
- `dz23-autonomous-improvement-ultimate` **2.1.0 → 2.1.1**: `evals/evals.json` estava no schema antigo
  (`prompt` + `expectations`), enquanto as outras 8 skills usam `input`/`expected`/`fails_if`. Isso gerava
  **36 problemas** no `check-structure` e quebrava qualquer harness que lesse só aquela skill. Os 12 casos
  foram migrados preservando conteúdo, e cada um ganhou `fails_if` (antes inexistente).
- README: seção de qualidade, tabela de ferramentas, documentos do repositório e aviso de evals reescrito
  com o número real (3 de ~137).

### Estado de verificação
- `python scripts/quality-gate.py` → **12/12 checks passaram** (local, Windows).
- `CI no GitHub`: workflow **nunca executou** — primeiro run acontece no próximo push. Declarado como
  dívida #3 no `ROADMAP.md`.

## [1.2.0] — 2026-11-09

### Adicionado
- **`external/ui-ux-pro-max.md`** — skill de design intelligence da nextlevelbuilder (MIT, 192 regras de
  raciocínio, 80 estilos de UI). Preenche o gap de **direção visual por segmento** antes do código.
- **`skills/dz23-ultimate-pro-max/references/stack-implementation.md`** (v2.1.0 → **2.2.0**) — tokens em 3
  camadas → Tailwind, adoção de shadcn/ui, estados obrigatórios por componente, especificidades
  React/Next/Vue/Nuxt/RN/Flutter, 8 bugs visuais recorrentes e checklist pré-e2e.
- **`skills/dz23-backend-data-architect/references/threat-modeling-and-appsec.md`** (v1.0.1 → **1.1.0**) —
  threat model em 6 passos, STRIDE com controle e teste por ameaça, OWASP Top 10 → controle verificável,
  ASVS L2, segredos/dependências/upload, hardening e gates de AppSec que bloqueiam merge.
- `VERSION` da `dz23-ultimate-pro-max` — existia só no frontmatter, o que quebrava empacotamento.

### Corrigido (diagnóstico do usuário, com ressalvas)
- O diagnóstico dizia que **faltava skill de frontend/UI**. Não faltava: `dz23-ultimate-pro-max` já
  existia (8 references, gates de acessibilidade e QA visual). Faltava **instanciação por stack** —
  resolvida com `stack-implementation.md`.
- O diagnóstico dizia que **filas/webhooks não estavam cobertos**. Estavam, em
  `references/service-architecture.md` (idempotency key, outbox, DLQ, retry com backoff+jitter, dedup de
  webhook, `SKIP LOCKED`). Nada a criar; só registro aqui para não duplicar.
- Gap **real** identificado: **AppSec ofensivo** (threat modeling/OWASP/ASVS) — fechado nesta versão.
- `external/superpowers.md` atualizado: licença MIT verificada, suporte multi-harness documentado
  (plugins `.codex-plugin`, `.cursor-plugin`, `.opencode`, `.pi`…), diagrama de pipeline.

### Estado de verificação
- `validate_skill.py` PASS nas duas skills alteradas · `skills-check.py` 0 erros · 9/9 skills `EM_DIA`
  contra o pacote publicado (`audit-zips.py`).
- Evals: continuam `NOT_TESTED` — nenhum dos ~125 cenários foi executado.

## [1.1.0] — 2026-11-08

### Adicionado
- **`prompts/`** — pasta para os prompts de origem das skills:
  - `prompts/performance-4-camadas.md` — prompt original em 4 camadas / 20 itens que deu origem à
    `dz23-performance-scalability-engine`, copiado **verbatim** (inclusive o typo "Processamento
    Assalariado", que a skill interpreta como assíncrono)
  - `prompts/README.md` — índice, comparação prompt × skill e regra de contribuição

## [1.0.0] — 2026-11-08

Primeira release pública.

### Adicionado
- **9 skills DZ23** em `skills/`:
  - `dz23-autonomous-improvement-ultimate` 2.1 — loop autônomo de correção
  - `dz23-backend-data-architect` 1.0.1 — backend, banco, contratos, migrações
  - `dz23-codebase-cartographer` 1.1.0 — mapeamento de codebase
  - `dz23-devops-cloud-deployer` 1.2.1 — DevSecOps, containers, CI/CD, IaC
  - `dz23-e2e-browser-verifier` 1.1.0 — E2E com Playwright + a11y
  - `dz23-performance-scalability-engine` 1.3.0 — otimização em 4 camadas
  - `dz23-reverse-engineer-anything` 1.1.1 — RE de binários e firmware
  - `dz23-spec-to-system-engine` 1.2.0 — especificação executável
  - `dz23-ultimate-pro-max` 2.1 — frontend, UI/UX, design system
- **1 MCP** em `mcp/dz23-subagents-universal-mcp/` (v4.4.1, 28 tools)
- **1 bundle** em `bundle/dz23-dsh-agency/` (v1.0.0, 88 agentes)
- **8 referências externas** em `external/` (Superpowers, REA, Cloudflare, Anthropic, Vercel,
  Supabase, Playwright MCP, Terraform AWS VPC)
- **Guia de CLIs** em `cli/` — inventário real da máquina, faltantes por prioridade, instalação por SO
- **Documentação** em `docs/` — getting started, overview, mapa de integração, instalação, FAQ
- **Scripts** em `scripts/` — `install-all.ps1`, `install-all.sh`, `audit-zips.py`, `verify-cli.ps1`

### Estado de verificação (honesto)
- **Integridade dos pacotes**: ✅ verificada — cada skill em `skills/` foi extraída do zip publicado e
  comparada por hash contra a skill instalada (0 divergências no momento da montagem).
- **Exemplos dos READMEs**: ⚠️ comandos verificados quanto a existência/sintaxe, **não** executados em
  todos os ambientes (Windows testado; Linux/Mac não).
- **Evals das skills**: ❌ **`NOT_TESTED`** — dos ~125 cenários declarados entre as 9 skills, apenas 3
  foram executados em harness real até esta release. Ver o `CHANGELOG.md` de cada skill.
- **Scripts das skills**: parcialmente testados — os que têm `selftest` (ex.: `re_toolkit.py`, 15/15)
  rodaram; o restante é `NOT_TESTED`.

### Limitações conhecidas
- As skills foram escritas e validadas primariamente em **Windows + PowerShell**; os caminhos Linux/Mac
  dos instaladores não foram exercitados.
- O bundle `dz23-dsh-agency` gera `agents/` via `build.py`, que depende de Python 3.10+.
- O MCP requer `npm install` (150 arquivos, dependências declaradas em `package.json`).
