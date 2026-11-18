# Changelog — untangle-codebase

Histórico desta skill. O changelog do arsenal fica na raiz (`CHANGELOG.md`).

## [1.0.0] — 2026-11-18

### Adicionado
- Primeira incorporação ao arsenal da skill `untangle-codebase`, de `caldoai/skills` (**MIT**, lida no
  arquivo `LICENSE` da raiz; Copyright 2026 Maze). Conteúdo internalizado e adaptado ao rito do
  arsenal, não copiado byte a byte.
- `SKILL.md` com fluxo em 5 passos, regras inegociáveis (lista antes de mudar, uma correção por grupo
  de problemas, git como evidência, não alterar comportamento intencional), estados de evidência e
  veredito.
- `references/`: `method.md`, `defect-taxonomy.md`, `git-as-evidence.md`, `verification.md`.
- `templates/decision-log.md`: registro de decisão (problemas + a correção que resolve vários).
- `evals/evals.json`: 6 cenários (catalogar antes de editar, uma correção por grupo, preservar
  comportamento, perguntar pelos extras, git como evidência, veredito honesto). **`NOT_TESTED`** até
  execução registrada em harness real — ver `ROADMAP.md`.
- `scripts/validate_skill.py` + validadores comuns do arsenal; entra no `quality-gate.py` e no CI.

### Proveniência
Registrada em `metadata` do `SKILL.md` e em `dados-design/VENDOR.md`. Scripts, testes e fixtures da
skill de origem não foram trazidos; só a orientação, reescrita no formato do arsenal.
