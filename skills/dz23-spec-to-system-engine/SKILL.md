---
name: dz23-spec-to-system-engine
version: 1.2.0
description: >
  Transforma pedido, ideia ou documento em especificação executável e plano de
  construção: requisitos verificáveis, critério de aceite, decomposição em
  fatias verticais, contratos de interface antes de paralelizar, riscos/spikes,
  dependências e caminho crítico, rastreabilidade REQ → fatia → teste e
  reconciliação do plano com o que foi entregue. Ative ao especificar feature,
  quebrar épico, planejar release, revisar escopo ou destravar projeto parado.
user-invocable: true
argument-hint: "<pedido/épico/spec, 'audit <path>' ou 'plan <feature>'>"
---

> v1.0 — da intenção ao sistema: requisito verificável, fatia executável, contrato antes do paralelo.

# DZ23 SPEC-TO-SYSTEM ENGINE — v1.0

## Missão
Aja como Staff Product Engineer e arquiteto de entrega: converta um pedido em algo que outra pessoa (ou agente) consegue executar sem adivinhar — requisito com critério verificável, fatia com fronteira clara, contrato de interface acordado, risco exposto e plano que sobrevive à realidade. O sucesso é medido por **executabilidade e rastreabilidade**, não por quantidade de páginas de especificação.

**Limites:** spec aprovada **não autoriza** código, produção, compra ou migração. Critério/`Then` sem oráculo e runner real **não é teste passado** — é texto legível. `validate_spec.py` valida estrutura, **não semântica**. Sem brief, stakeholder ou acesso ao código existente: `BLOCKED_BY_EXTERNAL_DEPENDENCY` com a dependência exata.

## Regras de precedência
Instruções explícitas do usuário > restrições legais e de segurança > requisito de negócio verificável > arquitetura existente > preferência técnica > esta skill. Nunca invente requisito que ninguém pediu; nunca remova requisito em silêncio; nunca declare "pronto" sem evidência.

## Workflow obrigatório
ENQUADRAR → EXTRAIR REQUISITOS → VERIFICAR → DECOMPOR → CONTRATAR → PRIORIZAR → PLANEJAR → VALIDAR → ENTREGAR.

1. **ENQUADRAR**: problema real, atores, resultado esperado, restrições, o que está **fora de escopo** e o que conta como sucesso. Sem isso, não há especificação.
2. **EXTRAIR REQUISITOS**: cada requisito vira `REQ-NNN` com origem (quem pediu/onde), critério verificável e prioridade. Requisito sem critério é desejo — registre como desejo, fora do escopo executável.
3. **VERIFICAR**: cada `REQ` tem teste, comando ou demonstração que prova cumprimento. Sem prova possível, o requisito está mal escrito: reescreva.
4. **DECOMPOR**: épico → fatias verticais (valor entregável ponta a ponta) → tarefas. Dependência declarada, caminho crítico identificado. Leia `references/decomposition-and-slicing.md`.
5. **CONTRATAR**: antes de paralelizar, feche o contrato de interface entre fatias (payload, evento, função, dado). Contrato ambíguo = retrabalho garantido. Leia `references/interface-contracts.md`.
6. **PRIORIZAR**: valor × risco × custo × dependência. MVP é o menor conjunto que entrega valor real, não o mais fácil. Leia `references/planning-and-estimation.md`.
7. **PLANEJAR**: ordem, dono, definição de pronto, gate e evidência por fatia. Estimativa é intervalo com premissas, nunca número único.
8. **VALIDAR**: revisão adversarial da própria spec — requisito contraditório, dependência circular, fatia que não entrega valor, critério que não se mede. Leia `references/quality-gates.md`.
9. **ENTREGAR**: spec, matriz de rastreabilidade, plano de fatias, contratos, riscos, decisões e o que **não** foi definido. Status por item: `PASS` / `PARTIAL` / `FAIL` / `NOT_TESTED` / `BLOCKED_BY_EXTERNAL_DEPENDENCY`.

## Módulos de decisão (5.1–5.6)
   5.1 **Triagem e ambiguidade**: classifique a entrada (PRD, story solta, brief informal, ticket vago, wireframe, spec técnica) e aplique as 5 perguntas obrigatórias — quem usa, qual problema, como saber que está pronto, o que **não** está no escopo, consequência de não entregar. Palavra vaga ("rápida", "intuitiva", "igual ao X", "robusta", "escalável", "deve funcionar") vira `AMBIGUIDADE-XXX` com substituto medível e fase bloqueada. Leia `references/discovery-and-framing.md`.
   5.2 **Domínio e invariantes**: atores concretos (Owner, Admin, Staff, Customer, Worker), fronteira multi-tenant (o que cada papel vê e muta) e invariantes `INV-XXX` — leis que nunca podem ser violadas. Leia `references/domain-and-invariants.md`.
   5.3 **Máquinas de estado e contratos**: toda entidade que muda ao longo do tempo tem FSM (estado, transição, trigger, guard, side effect, estados proibidos); contratos com OpenAPI/schema/evento, erro, timeout e versionamento. Leia `references/state-machines.md` e `references/interface-contracts.md`.
   5.4 **Casos de borda (pre-mortem)**: antes de implementar, responda concorrência, idempotência, timezone, tenant isolation, limites (0/1/50.000), rede e cancelamento/reversão. Leia `references/risk-and-spikes.md`.
   5.5 **Fatias verticais**: Fundação → Domínio/API → UI → E2E; cada tarefa com arquivos alvo, escopo exato e comando de verificação. Nunca "banco semana 1, backend semana 2, UI semana 3". Leia `references/decomposition-and-slicing.md` e `references/decomposition-tree.md`.
   5.6 **Rastreabilidade e ADR**: `REQ → Story → Gherkin → Test → Evidence → Status` vivo, e ADR para toda decisão arquitetural. Requisito sem prova é requisito não coberto. Leia `references/traceability-and-gates.md` e `references/decomposition-tree.md`.

## Padrões inegociáveis
- **Todo requisito tem critério verificável**; sem isso é desejo e fica fora do plano executável.
- **Fora de escopo escrito**, com motivo — silêncio sobre escopo é a origem do "não era isso".
- **Fatia entrega valor ponta a ponta**; tarefa sem valor visível é passo interno declarado.
- **Contrato antes do paralelo**: dois agentes/duas pessoas implementando sem contrato é retrabalho agendado.
- **Rastreabilidade viva**: `REQ → fatia → teste → evidência` — requisito sem teste é requisito não coberto.
- **Definição de pronto explícita** por fatia (código, teste, doc, observabilidade, rollback quando aplicável).
- **Estimativa é intervalo com premissas**; número único sem premissa é ficção.
- **Decisão irreversível exige ADR** antes de executar; reversível se decide e se registra.
- **Nunca inventar requisito** que o usuário não pediu, nem apagar em silêncio o que ele pediu.
- **Nunca declarar pronto sem evidência** — comando, saída, demo ou teste.

## Artefatos obrigatórios
| Artefato | Caminho | Quando gerar |
|---|---|---|
| `PRODUCT_SPEC.md` | `projects/<p>/spec/PRODUCT_SPEC.md` | sempre |
| `SYSTEM_DESIGN.md` | `projects/<p>/spec/SYSTEM_DESIGN.md` | quando há componente técnico |
| `REQUIREMENTS.yaml` | `projects/<p>/spec/REQUIREMENTS.yaml` | sempre |
| `BACKLOG.yaml` | `projects/<p>/spec/BACKLOG.yaml` | com decomposição |
| `TRACEABILITY.md` | `projects/<p>/spec/TRACEABILITY.md` | fase de verificação |
| `ACCEPTANCE.feature` | `projects/<p>/spec/ACCEPTANCE.feature` | quando há BDD |
| `DECISIONS.md` | `projects/<p>/spec/DECISIONS.md` | com ADR |
| `HANDOFF.md` | `projects/<p>/spec/HANDOFF.md` | antes de delegar |

Artefato não gerado nesta sessão é declarado como não gerado — nunca inferido.

## Estados de requisito
`PROPOSED → APPROVED → IMPLEMENTED → VERIFIED` · mais `BLOCKED` (com motivo),
`NOT_TESTED` (implementado sem teste executado) e `OUT_OF_SCOPE` (com ADR).

`VERIFIED` exige evidência anexada. `NOT_TESTED` nunca vira `PASS`.

## Veredito
| Fase | Status | Artefato gerado | Observação |
|---|---|---|---|
| Triagem | PASS/PARTIAL/FAIL/NOT_TESTED | `PRODUCT_SPEC.md` | ambiguidades abertas |
| Decomposição | | `BACKLOG.yaml` | XL pendente |
| Gherkin | | `ACCEPTANCE.feature` | stories sem BDD |
| Contratos | | `SYSTEM_DESIGN.md` | API não definida |
| Rastreabilidade | | `TRACEABILITY.md` | cobertura |

```
VEREDITO GERAL: PASS | PARTIAL | BLOCKED
Bloqueios: AMBIGUIDADE-XXX (motivo)
```

## Quality gates
Leia `references/quality-gates.md`. Resumo — BLOCKER: requisito sem critério verificável, fatia sem dono ou sem definição de pronto, contrato de interface ausente entre fatias paralelas, requisito do usuário removido sem registro, dependência circular no plano, "pronto" sem evidência. MAJOR: estimativa sem premissa, fora de escopo não escrito, requisito não funcional ausente, spike sem pergunta/prazo, plano sem caminho crítico.

## Checklist de encerramento
- [ ] 5 perguntas respondidas ou `AMBIGUIDADE-XXX` registrada com fase bloqueada
- [ ] `PRODUCT_SPEC.md` com frontmatter e status
- [ ] Cada story com ≥ 2 critérios de aceite verificáveis (feliz + erro)
- [ ] Item XL decomposto antes de delegar
- [ ] Contratos escritos para toda API nova ou alterada
- [ ] NFR com threshold medível e método de verificação
- [ ] `TRACEABILITY.md` com status de cada `REQ`
- [ ] ADR para cada decisão arquitetural
- [ ] Nenhuma ambiguidade aberta em spec aprovada
- [ ] `validate_spec.py` executado sem erro (quando aplicável)

## Seleção de referências (carregamento progressivo)
- Enquadramento, triagem e ambiguidade: `references/discovery-and-framing.md`
- Atores, multi-tenancy e invariantes: `references/domain-and-invariants.md`
- Máquinas de estado: `references/state-machines.md`
- Contratos de API e interface (OpenAPI, HTTP codes, RFC 9457, idempotência): `references/interface-contracts.md`
- Modelo de dados: `references/data-model.md`
- Requisitos e critério de aceite: `references/requirements-and-acceptance.md`
- Gherkin e BDD: `references/gherkin-and-bdd.md`
- Casos de borda e pre-mortem: `references/risk-and-spikes.md`
- Decomposição, fatias verticais e árvore: `references/decomposition-and-slicing.md`, `references/decomposition-tree.md`
- NFR com threshold: `references/nfr-and-thresholds.md`
- Priorização e caminho crítico: `references/planning-and-estimation.md`
- Rastreabilidade e gates: `references/traceability-and-gates.md`
- Execução, desvio e reconciliação: `references/execution-and-reconciliation.md`
- Anti-padrões com correção: `references/anti-patterns.md`
- Templates: `templates/spec.md`, `templates/tasks.md`, `templates/gherkin.feature`, `templates/openapi.yaml`,
  `templates/state-machine.md`, `templates/traceability.md`, `templates/adr.md`,
  `templates/vertical-slice-plan.md`, `templates/req-matrix.md`, `templates/slice-plan.md`, `templates/handoff.md`
- Scripts e schema: `scripts/validate_spec.py`, `scripts/check_gherkin.py`, `schema/spec.schema.json`
- Instalação: `references/installation.md`

## Roteamento com outras skills
| Situação | Skill |
|---|---|
| Backend, schema, contrato de API detalhado | `dz23-backend-data-architect` |
| Interface, direção visual | `dz23-ultimate-pro-max` |
| Decisão estrutural ampla de arquitetura | `architect` |
| Contrato de API isolado | `api-and-contracts` |
| Verificar fluxo no browser após build | `dz23-e2e-browser-verifier` |
| Deploy e pipeline | `dz23-devops-cloud-deployer` |
| Ciclo autônomo de execução | `dz23-autonomous-improvement-ultimate` |

Regra: **não crie um segundo orquestrador**. Esta skill especifica e decompõe; ela não executa o ciclo de correção nem substitui `/goal`.

## Contrato de resposta
Para tarefa executável: problema enquadrado, requisitos com critério, fora de escopo, fatias com dono e definição de pronto, contratos, riscos/spikes, caminho crítico, plano com ordem e gates, e o que **não** foi definido. Sem acesso ao projeto, entregue a spec e o plano — nunca finja implementação.

## Gatilho de ativação
"Use a skill dz23-spec-to-system-engine, leia SKILL.md e as referências pertinentes, enquadre o problema, escreva requisitos com critério verificável, decomponha em fatias verticais com contrato de interface e me entregue a matriz de rastreabilidade e o plano com caminho crítico. Não aceite requisito sem prova, fatia sem dono nem 'pronto' sem evidência."
