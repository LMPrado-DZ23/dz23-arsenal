# Skills overview — tabela comparativa

## Visão por eixo

| Skill | Precede | Sucede | Produz artefato? | Exige ambiente real? |
|---|---|---|---|---|
| `spec-to-system-engine` | — | backend, frontend | spec, fatias, Gherkin | não |
| `codebase-cartographer` | backend, frontend | — | mapa, evidence ledger | lê o repo |
| `backend-data-architect` | spec | devops | código, schema, ADR | sim (DB) |
| `ultimate-pro-max` | spec | e2e | UI, design system | sim (browser) |
| `devops-cloud-deployer` | backend | e2e | imagem, pipeline, IaC | sim (Docker/K8s) |
| `e2e-browser-verifier` | devops | — | trace, screenshot, veredito | sim (browser) |
| `performance-scalability-engine` | devops | — | budget, benchmark | sim (medição) |
| `reverse-engineer-anything` | — | cartographer | relatório, mapa de firmware | arquivo local |
| `autonomous-improvement-ultimate` | orquestra todas | — | checkpoint, log de rodadas | conforme a skill chamada |

## Complexidade e custo

| Skill | Complexidade | Custo de rodar | Quando o custo não se paga |
|---|---|---|---|
| `spec-to-system-engine` | intermediate | baixo (é raciocínio) | tarefa de 5 minutos |
| `codebase-cartographer` | intermediate | médio (lê muitos arquivos) | repo de 3 arquivos |
| `backend-data-architect` | advanced | alto (testes, DB) | ajuste de 1 linha |
| `ultimate-pro-max` | advanced | alto (browser, screenshots) | correção de texto |
| `devops-cloud-deployer` | advanced | alto (build, cluster) | projeto sem deploy |
| `e2e-browser-verifier` | intermediate | alto (Playwright) | fluxo sem UI |
| `performance-scalability-engine` | advanced | alto (medição real) | antes de ter baseline |
| `reverse-engineer-anything` | advanced | médio (ferramentas locais) | código-fonte disponível |
| `autonomous-improvement-ultimate` | advanced | alto (muitas rodadas) | tarefa única e simples |

## Sobreposições (e como resolver)

| Par | Risco de sobreposição | Regra de desempate |
|---|---|---|
| `backend-data-architect` × `spec-to-system-engine` | ambos modelam requisitos | spec **decide o quê**; backend **decide como** |
| `ultimate-pro-max` × `e2e-browser-verifier` | ambos tocam UI | ultra-pro-max **constrói**; e2e **verifica** |
| `devops-cloud-deployer` × `performance-scalability-engine` | ambos olham produção | devops **entrega**; performance **mede e corta** |
| `codebase-cartographer` × `reverse-engineer-anything` | ambos exploram | cartographer = **código**; RE = **artefato compilado** |
| `autonomous-improvement-ultimate` × todas | orquestração | ele **não implementa**; delega e cobra evidência |

## Estado real (não o ideal)

| Skill | Evals declarados | Executados | Cobertura |
|---|---|---|---|
| `autonomous-improvement-ultimate` | 12 | 1 | ~8% |
| `backend-data-architect` | 12 | 0 | 0% |
| `codebase-cartographer` | 15 | 0 | 0% |
| `devops-cloud-deployer` | 15 | 3 | 20% |
| `e2e-browser-verifier` | 15 | 0 | 0% |
| `performance-scalability-engine` | 16 | 3 | ~19% |
| `reverse-engineer-anything` | 15 | 0 | 0% |
| `spec-to-system-engine` | 15 | 0 | 0% |
| `ultimate-pro-max` | 0 | 0 | — |

Números verificados contra os `evals/evals.json` de cada skill. "Executado" significa rodado em harness
real e julgado; os demais são `NOT_TESTED`.
