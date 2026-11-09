# DZ23 Spec-to-System Engine v1.0.0

Skill de especificação executável e decomposição de produto para DeepSeek Harness e agentes compatíveis
com `SKILL.md`.

Cobre o caminho completo: **enquadrar → extrair requisitos → verificar → decompor → contratar → priorizar
→ planejar → validar → entregar**.

## Conteúdo

| Arquivo | Para quê |
|---|---|
| `SKILL.md` | Missão, workflow em 9 etapas e módulos 5.1–5.6 |
| `references/discovery-and-framing.md` | Triagem, 5 perguntas, detector de ambiguidade, escopo |
| `references/domain-and-invariants.md` | Atores, fronteira multi-tenant, `INV-XXX` |
| `references/state-machines.md` | FSM: estados, transições, guard, side effect, proibições |
| `references/interface-contracts.md` | OpenAPI 3.1, códigos HTTP, RFC 9457, idempotência, paginação |
| `references/data-model.md` | Entidade, tipos, constraints, índices, auditoria |
| `references/requirements-and-acceptance.md` | `REQ`, critério verificável, caminho infeliz, conflitos |
| `references/gherkin-and-bdd.md` | Feature/Scenario/Outline, regra 1 feliz + 2 erros, binding E2E |
| `references/risk-and-spikes.md` | Risco, spike e **pre-mortem** (concorrência, tenant, reversão) |
| `references/decomposition-and-slicing.md` | Fatias verticais e os 4 estágios (Fundação → E2E) |
| `references/decomposition-tree.md` | EPIC → FEATURE → STORY → TASK, regra XL, INVEST |
| `references/nfr-and-thresholds.md` | NFR com threshold medível e método de verificação |
| `references/planning-and-estimation.md` | Priorização, intervalo com premissa, caminho crítico |
| `references/traceability-and-gates.md` | `REQ → Story → Gherkin → Test → Evidence → Status` |
| `references/execution-and-reconciliation.md` | Reconciliar plano com realidade; desvio registrado |
| `references/anti-patterns.md` | 32 erros recorrentes com correção |
| `references/quality-gates.md` | Gates e severidade (BLOCKER/MAJOR/MINOR) |
| `references/installation.md` | Instalação e quando **não** usar |
| `templates/spec.md` | `PRODUCT_SPEC` (problema → decisões → não definido) |
| `templates/tasks.md` | `BACKLOG`: EPIC → FEAT → STORY (CA) → TASK (≤4h) |
| `templates/gherkin.feature` | Feature + Background + cenários feliz/erro/borda/autorização |
| `templates/openapi.yaml` | OpenAPI 3.1 com erro RFC 9457, idempotência e rate limit |
| `templates/state-machine.md` | Tabela de estados, transições e proibições |
| `templates/traceability.md` | Matriz de rastreabilidade com legenda de status |
| `templates/adr.md` | ADR (contexto, opções, decisão, consequências) |
| `templates/vertical-slice-plan.md` | DAG dos 4 slices com DoD e comando de verificação |
| `examples/spec-example.json` | Manifesto válido contra o schema (fixture, não template) |
| `scripts/validate_skill.py` | Validador do pacote (refs, templates, evals, versão) |
| `scripts/validate_spec.py` | Valida manifesto contra o schema + IDs/DAG/ciclo (estrutural) |
| `scripts/check_gherkin.py` | Verifica estrutura do `.feature` |
| `schema/spec.schema.json` | JSON Schema 2020-12 do manifesto de spec |

## Escopo

Instruções e metodologia. Não escreve código nem substitui `dz23-backend-data-architect`,
`dz23-ultimate-pro-max` ou `dz23-devops-cloud-deployer`: ela produz a spec, o plano e os contratos que
essas skills executam. Exige evidência — requisito sem prova não entra em `READY`.

## Uso

1. Instalar no diretório de skills (`references/installation.md`).
2. Invocar por `/dz23-spec-to-system-engine` ou por descrição ("quebre este épico em fatias com contrato").
3. Artefatos vão para `projects/<projeto>/spec/`, não para a pasta da skill.

**Prompt de ativação:** [`PROMPT-ATIVACAO.txt`](PROMPT-ATIVACAO.txt).

**Avaliação:** `evals/evals.json` — 15 cenários (schema 1). Cenários não são testes executados: rode em
harness real e registre o resultado por caso.

**Versão:** [`VERSION`](VERSION) (1.0.0) · histórico em [`CHANGELOG.md`](CHANGELOG.md).

## Princípio

Requisito sem prova é desejo; plano sem contrato é retrabalho; `DONE` sem evidência é ficção.

---

## Arsenal — resumo operacional

**Versão real (VERSION/frontmatter):** 1.2.0 · **Categoria:** orchestration · **Complexidade:** intermediate

### Quando usar

- Transformar pedido, ideia ou documento em especificação executável.
- Quebrar épico em fatias verticais entregáveis.
- Definir critério de aceite verificável antes de implementar.
- Reconciliar o plano com o que foi realmente entregue.

### Quando NÃO usar

- Implementar — ela especifica; quem constrói é a skill de domínio.
- Tarefa de 5 minutos com requisito óbvio.
- Quando não há ninguém para validar a spec com o solicitante.

### Instalação

```bash
# Já incluída no install-all. Manual:
cp -r skills/dz23-spec-to-system-engine ~/.agents/skills/dz23-spec-to-system-engine
```

### Uso

```bash
/dz23-spec-to-system-engine

# ou por descrição — o agente carrega sozinho (ver SKILL.md)
```

### Pré-requisitos de CLI

`git` (obrigatória) · `python` (recomendada, para validadores).

### Evidência / Quality gates

- Todo requisito com critério de aceite verificável e rastreabilidade REQ → fatia → teste.
- Contrato de interface acordado antes de paralelizar trabalho.
- Dependências e caminho crítico declarados.
- O que está fora de escopo é explícito.

### Integração com outras skills

Alimenta `dz23-backend-data-architect` e `dz23-ultimate-pro-max`; é orquestrada por `dz23-autonomous-improvement-ultimate`.

### Versão e changelog

Ver [`CHANGELOG.md`](CHANGELOG.md) (desta skill) e o histórico do arsenal em [`../../CHANGELOG.md`](../../CHANGELOG.md).
