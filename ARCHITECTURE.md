# Arquitetura — dz23-arsenal

Mapa honesto das camadas do mandato contra o que **existe de fato** no repositório. Legenda:
**EXISTE** (implementado e verificado no gate) · **PARCIAL** (existe, incompleto) · **PLANEJADO**
(ainda não criado).

| # | Camada (mandato) | Estado | Onde está hoje |
|---|---|---|---|
| 1 | `core/` — contratos, tipos, runtime mínimo | **PARCIAL** | não há pasta `core/`; o núcleo é `scripts/` (gate + 109 verificadores), `arsenal.json` (manifesto), `evals.schema.json` (contrato de eval) |
| 2 | `skills/` | **EXISTE** | 18 skills, cada uma com `SKILL.md`, `validate_skill.py`, evals; índice gerado (`gera-indice-skills.py`) |
| 3 | `mcp/` | **EXISTE** | `pentagi-mcp` (selftest acionável) e `dz23-subagents-universal-mcp` (293 testes, zero deps) |
| 4 | `agents/` | **PARCIAL** | `bundle/dz23-dsh-agency/` (agents gerados + `build.py --check`); não há pasta `agents/` de topo |
| 5 | `adapters/` — integrações opcionais | **PLANEJADO** | hoje são **REFERÊNCIA** no catálogo (Ollama, Playwright MCP, LiteLLM…); nenhum adaptador testado ainda |
| 6 | `catalog/` | **EXISTE** | `catalog/catalog.json` (35 fontes) → `CATALOG.md`, `THIRD-PARTY.md`, `LICENSE-MATRIX.md` gerados; `external/*.md` com o cuidado por fonte |
| 7 | `providers/` — locais e externos | **PLANEJADO** | execução local existe via skills (`m920q-ai`, `sd-local`); não há camada `providers/` dedicada |
| 8 | `evaluations/` | **PARCIAL** | `eval-harness/` (replay determinístico, 8 reproduzíveis), `evals-results/` (laudos), `evals.schema.json`, `skills/*/evals/` |
| 9 | `install/` | **EXISTE** | `install/README.md` + `scripts/dz23-install.py` (detect, dry-run, offline, manifesto, rollback, log sem segredo) |
| 10 | `docs/` | **EXISTE** | `docs/` + docs de raiz (README, ARCHITECTURE, SECURITY, LIMITATIONS, THIRD-PARTY, LICENSE-MATRIX…) |
| 11 | `supply-chain/` | **EXISTE** | `supply-chain/sbom.json` + `SBOM.md` (CycloneDX das deps diretas) + CI: Dependabot, Gitleaks, CodeQL |
| + | `security/` (regra 7) | **EXISTE** | `security/permissoes.json` → `PERMISSIONS.md`: permissões/riscos/dry-run/rollback/aprovação das 18 skills |

## Princípio de verificação

Nada é "pronto" sem um verificador no gate. `scripts/quality-gate.py` roda **109 checks** (um comando,
um veredito) e é o umbrella de: validação de cada skill, coerência e citações de evals, estrutura,
links, higiene de docs, números, licenças, segredos, cópias embutidas, SBOM, catálogo, permissões,
instalador, replay de eval, e os selftests (controle negativo) de cada verificador novo. O gate roda
**offline** e é validado em **Ubuntu e Windows** no CI (o job Windows existe porque o bug de encoding
cp1252 só aparecia lá).

## Camadas geradas de fonte única (não apodrecem)

Vários documentos são **gerados** de um JSON e conferidos por `--check` no gate — editar à mão quebra
o CI:

- `catalog/catalog.json` → `CATALOG.md`, `THIRD-PARTY.md`, `LICENSE-MATRIX.md` (`gera-catalog.py`)
- `security/permissoes.json` → `PERMISSIONS.md` (`gera-permissoes.py`)
- `mcp/*/package.json` → `supply-chain/sbom.json` + `SBOM.md` (`gera-sbom.py`)
- `skills/*/` → `skills/README.md` (`gera-indice-skills.py`)

## O que a arquitetura NÃO afirma

Não há camada que torne o arsenal "universal" ou "superior a tudo". Integrações externas
(`adapters/`, `providers/`) são **REFERÊNCIA** até terem adaptador **com requisito + teste**; enquanto
isso, cada skill que depende de ferramenta externa declara `NOT_TESTED/BLOCKED` sem a ferramenta.
Ver [`LIMITATIONS.md`](LIMITATIONS.md) e [`matriz-de-requisitos.md`](matriz-de-requisitos.md).
