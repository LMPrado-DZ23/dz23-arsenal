# Changelog — dz23-performance-scalability-engine

## [1.3.0] — 2026-11-08

Dois fixes de auditoria: **F-9** (eval impossível de cumprir) e **F-5** (scripts não documentados no
`SKILL.md`). Nenhuma regra de julgamento mudou; nenhuma reference removida.

### Corrigido
- **F-9 — eval `optimize-without-baseline` era autocontraditório.** O `expected` exigia *"entrega baseline
  por camada"*, mas o `input` declara *"nenhuma medição"* — cumprir à risca exigiria **inventar número**,
  violando o padrão inegociável da própria skill. Novo `expected`:
  > "Recusa cortar antes de medir. Define instrumento, ambiente e janela de medição. Declara
  > `BLOCKED_BY_EXTERNAL_DEPENDENCY` se não houver acesso a ambiente real; **propõe** baseline a ser medido,
  > sem inventar número."

  Agora aceita as duas respostas válidas: (a) pedir acesso e bloquear, (b) propor plano de medição.
  `fails_if` mantido sem alteração.
- **F-5 — `SKILL.md` citava 2 dos 4 scripts.** `compare_samples.py` e `check_budget.py` existiam no disco,
  no `README` e no validador, mas não na lista de scripts do `SKILL.md` — o agente que carrega a skill não
  descobria as ferramentas que sustentam os padrões "prova antes/depois" e "budget declarado".
  - `SKILL.md` L157 agora lista os 4: `web_vitals_probe.py`, `compare_samples.py`, `check_budget.py`,
    `validate_skill.py`.
  - `references/perf-budget.md` ganhou a seção **"Verificação automatizada do budget"**, documentando
    `check_budget.py` (que não era citado em nenhuma reference), com exit codes e o aviso de que ele não mede.

### Nota
- O `audit-package/` foi **re-congelado como v1.1.1** para levar o `expected` corrigido. Essa v1.1.1 é um
  rótulo **artificial de snapshot** — nunca houve release v1.1.1 desta skill (foi 1.0.0 → 1.1.0 → 1.2.0 →
  1.3.0). Registrado no `FREEZE.md` do pacote para não gerar confusão futura.

### Validação
- `validate_skill.py`: PASS (10 refs + 6 templates + 4 scripts; 16 evals; frontmatter v1.3.0).
- `skills-check.py`: 0 erros.
- Nenhum eval executado nesta rodada.

## [1.2.0] — 2026-11-08

Fecha os 3 gaps da rodada de evals (2 achados na re-auditoria + 1 lacuna de cobertura). Nenhum eval foi
executado nesta rodada; `references/` não foi tocado.

### Adicionado
- **Regra F-1** (`SKILL.md`, §Pré-condições): `ALVO` inferido deve ser marcado **`(a confirmar)`**. Se o
  usuário não declarou a rota/handler/serviço, o agente não pode assumir — atribuir alvo ao pedido viola a
  separação observado × inferido (§5.6).
- **Regra F-2** (`SKILL.md`, §Pré-condições): pré-condições devem carregar o que está sendo proposto —
  `THRESHOLD: proposta inicial: p95 ≤ 300 ms`, nunca `NÃO DECLARADO` com a proposta escondida em outra
  seção. Contradição interna é bug de execução.
- **Eval `claims-faster-without-command`** (16º caso): "ficou 40% mais rápido, fecha aí" → exige comando +
  workload + percentil + volume; sem isso, `NOT_TESTED`.
- **Pacote de auditoria independente** em `projects/eval-performance/audit-package/` (7 arquivos):
  3 respostas, `evals.json`, `SKILL.md`, `rubrica-em-branco.md` e `README.md` com o que **não** deve ser
  passado ao auditor.

### Corrigido
- **F-1** — `response-1.txt` escrevia `ALVO: rota /orders (do pedido)` quando o `input` não citava endpoint:
  inferência apresentada como fato.
- **F-2** — `response-1.txt` dizia `THRESHOLD: NÃO DECLARADO` e propunha `p95 ≤ 300 ms` em outra seção.
- **Lacuna de cobertura** — não existia cenário de "alegação de ganho sem comando nenhum"; o mais próximo
  (`before-after-different-env`) cobria comparação inválida, não a ausência total de medição.

### Validação
- `validate_skill.py`: PASS (10 refs + 6 templates + 4 scripts; **16 evals**; frontmatter v1.2.0).
  O validador foi ajustado de 15 → 16 casos.
- `skills-check.py`: 0 erros.
- Nenhum eval rodado nesta rodada; 16 casos seguem `NOT_TESTED` até execução em harness real.

## [1.1.0] — 2026-11-08

Merge de 3 propostas (Gemini / Claude / ChatGPT) + relatório Manus sobre a spec original do usuário
(4 camadas × 20 itens). Fontes preservadas em `projects/dz23-performance-scalability-engine/_sources/`.

### Adicionado
- `references/diagnostic-playbook.md` — sintoma → camada provável → primeira medição, bisecção em 4
  medições e árvore de decisão
- `templates/diagnosis-report.md` — baseline por camada com budget e gargalo localizado
- `templates/adr-performance.md` — ADR de trade-off de performance com medição
- `scripts/compare_samples.py` — reimplementação mínima do Manus: percentis nearest-rank, bloqueia
  comparação com metadata divergente (exit 3), flags `performance_pass=false`
- `scripts/check_budget.py` — parser budget × benchmark (não mede nada), exit 0/1/2
- SKILL.md: pré-condições (ALVO/BASELINE/THRESHOLD/CAMADA/BLOQUEIOS), tabela 4×20 com link por item,
  5 entregáveis obrigatórios, guardrails de segurança, veredito e checklist de 10

### Expandido
- `backend-layer.md`: nota HTML no topo sobre o typo "Assalariado" → "assíncrono"
  (spec original preservada em `_sources/user-spec.md`)
- `measurement-first.md`: seção "Comparação de amostras" com `compare_samples.py`
- `perf-budget.md`: matriz ICE (impacto × esforço) com tabela de ordenação

### Preservado
- 9 refs (`measurement-first`, `perf-budget`, `frontend-layer`, `network-layer`, `backend-layer`,
  `infra-layer`, `anti-patterns`, `quality-gates`, `installation`) — nenhum renomeado
- 4 templates (`perf-plan`, `layer-checklist`, `perf-budget`, `benchmark-report`)
- 2 scripts (`web_vitals_probe.py`, `validate_skill.py`) e 15 evals
- workflow e gates

### Nota
- `compare_samples.py` é reimplementação mínima (Manus em sandbox; 46 testes não portados):
  flags `performance_pass=false`, `benchmark_executed=false`, `context_verified=false`
- Grafia do CLS no `gemini.md` verificada: **`CLS < 0.05`** (ponto decimal) — usada na reference
- `_sources/user-spec.md` foi salvo do histórico do chat, não de arquivo em disco
- Correção de encoding: ambos os scripts novos reconfiguram stdout para UTF-8 (console Windows cp1252
  quebrava ao imprimir `≤` e `Δ`)

## [1.0.0] — 2026-11-08

Primeira versão. Plano cirúrgico de performance e escalabilidade em 4 camadas, com
**problema que evita · como implementar · diretriz técnica** para cada um dos 20 itens.

- `SKILL.md`: missão, workflow em 6 etapas (MEDIR → LOCALIZAR → ORÇAR → CORTAR → VERIFICAR → GUARDAR)
  e módulos 5.1–5.6 (medição, 4 camadas, verificação/guarda).
- 9 references:
  - `measurement-first.md` — baseline por camada, percentis, sintético × RUM, teste de carga, armadilhas
  - `perf-budget.md` — tabelas de budget, priorização impacto ÷ esforço, custo, quando não fecha
  - `frontend-layer.md` — 7 itens da camada 1 com código real
  - `network-layer.md` — 4 itens da camada 2 com código real
  - `backend-layer.md` — 4 itens da camada 3 com SQL/ORM real
  - `infra-layer.md` — 5 itens da camada 4 com config de proxy/CDN/OTel
  - `anti-patterns.md` — 49 erros recorrentes com correção
  - `quality-gates.md` — 9 gates, severidade BLOCKER/MAJOR/MINOR, checklist de 11
  - `installation.md` — instalação, ferramental recomendado, quando não usar
- 4 templates: `perf-plan.md` (as 4 camadas × 20 itens com colunas de ganho/esforço),
  `layer-checklist.md`, `perf-budget.md`, `benchmark-report.md`.
- 2 scripts: `web_vitals_probe.py` (sonda HTTP read-only: TTFB, bytes, compressão, cache, CDN)
  e `validate_skill.py`.
- 15 cenários de avaliação em `evals/evals.json` (schema 1).
- Padrões inegociáveis: medir antes de otimizar, percentil e nunca média, um gargalo por vez,
  budget antes da mudança, atacar a camada do gargalo, nunca degradar correção, prova antes/depois
  com o mesmo instrumento, guarda de regressão, custo declarado.

### Validação do script
`web_vitals_probe.py` exercitado nesta máquina contra servidor HTTP local (`python -m http.server`):
resposta 200 com TTFB em ms, `p50/p95` em 3 execuções, e achados corretos de **FAIL** por ausência de
`Content-Encoding` e `Cache-Control`. Também testado contra endpoint que exige auth (HTTP 401 tratado
como falha de requisição, exit 1) e URL inválida (exit 2). O endpoint HTTPS público não foi testado
porque exige TLS válido — `NOT_TESTED`.
