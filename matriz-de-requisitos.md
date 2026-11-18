# Matriz de requisitos — mandato dz23-arsenal

Estado honesto de cada requisito do mandato, com critério verificável, evidência e estado.
Legenda: **PASS** (feito, com evidência) · **PARTIAL** (parcial) · **NOT_TESTED** (não exercitado) ·
**BLOCKED** (depende de fonte/infra/autorização externa).

## Fases 1–3 (auditoria, ferramentas, baseline)

| REQ | Critério | Evidência | Estado |
|---|---|---|---|
| R-01 Auditoria | estrutura, skills, MCPs, testes, remoto, árvore levantados | `auditoria-arquiteto-a89e6db.md`, `matriz-de-incorporacao.md` | **PASS** |
| R-02 Verificação de ferramentas | AVAILABLE/UNAVAILABLE por comando real | `dz23-install.py detect`; gate exercita python/node | **PARTIAL** (as exigidas por skill ficam `NOT_TESTED` sem a tool) |
| R-03 Baseline | gate + testes antes de alterar | gate `109/109` registrado antes de cada mudança | **PASS** |

## Fase 4 — P0

| REQ | Critério | Evidência | Estado |
|---|---|---|---|
| R-10 Catálogo externo verificável | índice máquina-legível + verificador | `catalog/catalog.json` (35 fontes) + `catalogo:*` no gate (commit `3149773`) | **PASS** |
| R-11 Instalador multiplataforma | detect, dry-run, offline, rollback, log sem segredo | `scripts/dz23-install.py` + `install:autoteste` (commit `08b84fb`) | **PASS** |
| R-12 OpenBot como integração opcional | sem danger-full-access automático, só catálogo | entrada no catálogo + `external/openbot.md`; **adaptador não feito** | **PARTIAL / BLOCKED** (sem fonte) |
| R-13 modern-web-guidance | licença verificada, incorporação | Apache-2.0 lido; harness de eval adaptado | **PARTIAL** |
| R-14 untangle-codebase adaptado | exige baseline/aprovação, não remove teste só | skill `untangle-codebase` + `prune-tests` (permissões declaram aprovação obrigatória) | **PASS** |
| R-15 MCP Inspector/Registry | integração | catalogados (REFERENCIA); sem adaptador | **BLOCKED** (sem fonte) |
| R-16 Ollama | integração local com fallback | catalogado (INTEGRAR_POR_ADAPTADOR); fallback `m920q-ai`/`sd-local` | **PARTIAL / BLOCKED** |
| R-17 Sistema de permissões | permissões/riscos/dry-run/rollback/aprovação por skill | `security/permissoes.json` + `permissoes:*` (commit `3ff71ce`) | **PASS** |
| R-18 SBOM + verificação de deps | SBOM real + scanner de dependência | `supply-chain/sbom.json` + Dependabot/Gitleaks/CodeQL (commits `fe47139`, `f614908`, `1019715`) | **PASS** |

## Fase 4 — P1 / P2

| REQ | Critério | Evidência | Estado |
|---|---|---|---|
| R-20 Harness de eval independente | prova reproduzível, separação de camadas | `eval-harness/` replay (8 reproduzíveis, 6 skills; commits `2a44446`, `156c746`) | **PARTIAL** (Camada 1-reproduzível; Camada 3 juiz externo = **NOT_TESTED**) |
| R-21 OpenHands/Pydantic/LangGraph/LiteLLM/Semantic Kernel | adaptador + fallback local | catalogados; sem adaptador | **BLOCKED** (sem fonte) |
| R-22 vLLM / SWE-agent / marketplace assinado | P2 | catalogados | **NOT_TESTED** |

## Fase 5 — Segurança (supply-chain + OWASP)

| REQ | Critério | Evidência | Estado |
|---|---|---|---|
| R-30 Segredos fora do versionado | scanner no gate + histórico | `check-secrets.py` (gate) + Gitleaks (CI) | **PASS** |
| R-31 SAST | análise estática de Python/JS | CodeQL (CI, 2 linguagens) | **PASS** |
| R-32 Dependências vulneráveis | acompanhamento | Dependabot (Actions + npm) | **PASS** |
| R-33 Prompt injection / conteúdo externo como DADO | regra aplicada nas skills | `master-engineer` §15; declarado nas skills | **PARTIAL** (instrução; não há teste automatizado dedicado) |
| R-34 OWASP app (IDOR, SSRF, path traversal…) | teste por alvo | sem skill SAST/DAST dedicada de aplicação | **NOT_TESTED** |

## Fase 6 — Evals reproduzíveis

| REQ | Critério | Evidência | Estado |
|---|---|---|---|
| R-40 Eval com objetivo/entrada/critério/evidência/limitações | ledger + replay | `evals.schema.json`, `evals-results/`, `eval-harness/` | **PARTIAL** (estrutura PASS; cobertura reproduzível = 8) |
| R-41 Uso offline / falha de dependência / recuperação | cenários cobertos | evals `blocked-secret`, `no-authorization`, install offline | **PASS** (amostra) |

## Fase 7 — Revisão

| REQ | Critério | Evidência | Estado |
|---|---|---|---|
| R-50 Segunda passada (regressão, segredo, licença, números) | revisão registrada | esta sessão: auto-revisão + gate; duas revisões externas endereçadas | **PARTIAL** (AUTO-REVISÃO; revisão independente por subagente = **NOT_TESTED**) |

## Entregáveis finais (docs)

| Documento | Estado |
|---|---|
| README, SECURITY, CONTRIBUTING, CHANGELOG | **PASS** (existiam) |
| CATALOG.md, THIRD-PARTY.md, LICENSE-MATRIX.md | **PASS** (gerados de `catalog.json`, `--check` no gate) |
| SBOM | **PASS** |
| ARCHITECTURE.md, LIMITATIONS.md, matriz-de-requisitos.md | **PASS** (este lote) |
| INSTALL.md / OFFLINE-MODE.md / EVALUATIONS.md / COMPATIBILITY.md | **PARTIAL** (conteúdo em `install/README.md` e `eval-harness/README.md`; docs dedicados ainda não) |

## Status geral: **PARTIAL**

P0 fundação (catálogo, SBOM, permissões, instalador, supply-chain CI) **PASS** com evidência e CI nos
2 SO. P1 iniciado (harness de eval reproduzível). Integrações externas e Camada 3 de eval seguem
**BLOCKED/NOT_TESTED** — declarado, não maquiado. Nenhuma afirmação de superioridade universal.
