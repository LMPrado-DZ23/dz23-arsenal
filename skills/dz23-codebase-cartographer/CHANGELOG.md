# Changelog — dz23-codebase-cartographer

## [1.1.0] — 2026-11-08

Merge das 3 propostas (Claude / Gemini / ChatGPT) + relatório Manus sobre a v1.0.0.
Fontes preservadas em `projects/dz23-codebase-cartographer/_sources/` (fora do pacote).

### Adicionado
- 4 references novos: `entrypoints-and-spine`, `context-budget`, `security-and-evidence`,
  `mapping-playbook`
- 3 templates: `EVIDENCE_LEDGER.md`, `AGENT_HANDOFF.md`, `context-pack.md`
- 1 script: `repo_inventory.py` (inventário Git mínimo do Manus — metadata only)
- SKILL.md: declaração de escopo (PERGUNTA/ALVO/BUDGET/SAÍDA), 5 entregáveis obrigatórios,
  estados de evidência, veredito e checklist de 10 itens
- Módulos 5.1–5.6 renumerados: reconhecimento, entrypoints/spine, data lineage, dependency
  graph/impact, context budget, evidence/handoff

### Expandido
- `discovery-scan`: topografia em 60s + bash concreto + git intelligence (hotspots, 14 dias, branches)
- `data-and-flow`: os 5 saltos explícitos (UI → API → controller/schema → service → persistence)
- `dependency-graph`: classificação de impacto ALTO/MÉDIO/BAIXO + callers/co-change

### Preservado
- 11 refs originais, 4 templates, 15 evals, `repo_probe.py`, `validate_skill.py`, workflow e gates

### Nota
- `repo_inventory.py` é reimplementação mínima (Manus em sandbox): helper completo com 36 testes não
  foi portado — regras finas `NOT_TESTED`. Validado em repo real (84 arquivos), dir não-git (exit 2),
  `--force` e exclusão de `.env`/`credentials`/`node_modules` mesmo com `--untracked`.
- `dz23-spec-to-system-engine` **não** foi atualizado para referenciar esta skill (v1.1.0 precisa
  estabilizar primeiro)

## [1.0.0] — 2026-11-08

Primeira versão. Skill de engenharia de contexto e mapeamento de codebase — a peça que faltava
nas propostas originais (era citada por Claude e ChatGPT como dependência e não existia no ambiente).

- `SKILL.md`: missão com limites (só lê), workflow em 7 etapas (ORIENTAR → MANTER) e módulos 5.1–5.6
  (inventário, dependências, dados, convenções, risco/dívida, contexto para agente).
- 11 references: varredura, grafo de dependências, dados e fluxo, convenções do repo, hot spots e dívida,
  zonas de risco, context brief, verificação/frescor, anti-padrões (30), quality gates, instalação.
- 4 templates: `codebase-map.md`, `context-brief.md`, `change-impact.md`, `hotspot-report.md`.
- 2 scripts: `repo_probe.py` (scanner read-only, com `--json`) e `validate_skill.py`.
- 15 cenários de avaliação em `evals/evals.json` (schema 1).
- Padrões inegociáveis: evidência por afirmação (`arquivo:linha`), observado × inferido × não verificado,
  mapa datado com commit, amostragem declarada, não editar código, brief com orçamento e ponteiros,
  "não tocar sem plano" como seção obrigatória.
- `repo_probe.py` validado em repositório real (`projects/ai-bridge/repo`: commit, branch, 81 arquivos,
  10.812 linhas, Python, CI detectado) e em diretório não-git.
