# Changelog — dz23-spec-to-system-engine

## [1.2.0] — 2026-11-08

### Corrigido
- Fixture `spec-example.json` movido de `templates/` para `examples/` (não é template; é dado de teste)
- `validate_spec.py` expandido para cobrir regras finas do Manus: IDs com whitespace/newline,
  `schema_version` boolean, JSON com chave duplicada, NaN/Infinity, input > 1 MiB, symlink final,
  permissões de output (N/A — o script não grava arquivo) e redação de erro (valores de ID não são
  ecoados; `<valor omitido>`)

### Nota
- 6 fixtures novos em `examples/` para testar as regras (5 executados; o de symlink é
  `BLOCKED_BY_EXTERNAL_DEPENDENCY` — Windows exige privilégio de administrador ou Developer Mode)
- `validate_skill.py`: `spec-example.json` saiu de `templates/`; `examples/` é opcional (não obrigatório)

## [1.1.0] — 2026-11-08

Merge das 3 propostas (Claude / Gemini / ChatGPT) + relatório de verificação Manus sobre a v1.0.0.
Fontes preservadas em `projects/dz23-spec-to-system-engine/_sources/` (fora do pacote).

### Adicionado
- 6 references novos: `domain-and-invariants`, `state-machines`, `data-model`, `gherkin-and-bdd`,
  `decomposition-tree`, `nfr-and-thresholds`
- 8 templates: `tasks`, `gherkin.feature`, `openapi.yaml`, `state-machine`, `traceability`, `adr`,
  `vertical-slice-plan`, `spec-example.json`
- 2 scripts: `validate_spec.py` (reimplementação mínima documentada) e `check_gherkin.py`
- `schema/spec.schema.json` (JSON Schema 2020-12)
- SKILL.md: Missão com limites explícitos, artefatos obrigatórios (8), estados de requisito,
  veredito por fase e checklist de encerramento (10 itens)
- Módulos 5.1–5.6 renumerados para: triagem/ambiguidade, domínio/invariantes, FSM/contratos,
  pre-mortem, fatias verticais, rastreabilidade/ADR

### Expandido
- `discovery-and-framing`: triagem por tipo de entrada, 5 perguntas obrigatórias, detector de
  ambiguidade e formato `AMBIGUIDADE-XXX`
- `interface-contracts`: OpenAPI 3.1, semântica de códigos HTTP (400×422, 401×403, 404 cross-tenant),
  envelope RFC 9457, idempotência, rate limit e paginação
- `risk-and-spikes`: pre-mortem (concorrência, idempotência, timezone, tenant, limites, rede, reversão)
- `decomposition-and-slicing`: fatias em 4 estágios (Fundação → Domínio/API → UI → E2E)
- `traceability-and-gates`: cadeia `REQ → Story → Gherkin → Test → Evidence → Status` com legenda

### Preservado
- 11 references originais, 4 templates, 15 evals, 32 anti-padrões, `validate_skill.py`, workflow e gates

### Nota
- `validate_spec.py` é reimplementação mínima (o original do Manus está em sandbox e não é recuperável);
  declara `behavior_verified=false`, `authorization_granted=false`, `runner_refs_verified=false`
- A skill de mapeamento de código citada pelas fontes (codebase cartographer) **não existe** neste
  ambiente — análise de código existente via `dz23-backend-data-architect`

## [1.0.0] — 2026-11-08

Primeira versão.

- `SKILL.md`: missão, precedência, workflow em 9 etapas (ENQUADRAR → ENTREGAR) e módulos 5.1–5.6
  (enquadramento, requisito verificável, decomposição, contrato de interface, risco/spike,
  execução/reconciliação).
- 11 references: descoberta e escopo, requisitos e aceite, fatiamento, contratos, risco/spike,
  priorização e caminho crítico, rastreabilidade e gates, execução/reconciliação, anti-padrões (32),
  quality gates e instalação.
- 4 templates: `spec.md`, `req-matrix.md`, `slice-plan.md`, `handoff.md`.
- 15 cenários de avaliação em `evals/evals.json` (schema 1).
- Padrões inegociáveis: requisito com critério verificável, fora de escopo escrito, fatia vertical com
  dono e DoD, contrato antes do paralelo, estimativa em intervalo com premissa, decisão irreversível com
  ADR, rastreabilidade `REQ → fatia → teste → evidência` e `DONE` só com prova.
- Quality gates com severidade BLOCKER/MAJOR/MINOR e matriz de verificação por artefato.
