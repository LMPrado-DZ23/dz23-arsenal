# Changelog — prune-tests

Histórico desta skill. O changelog do arsenal fica na raiz (`CHANGELOG.md`).

## [1.0.0] — 2026-11-18

### Adicionado
- Incorporação ao arsenal da skill `prune-tests`, de `caldoai/skills` (**MIT**, lida no arquivo
  `LICENSE` da raiz; Copyright 2026 Maze). Conteúdo internalizado e adaptado ao rito do arsenal, não
  copiado byte a byte.
- `SKILL.md`: diagnóstico por dependência; três famílias a podar (passado, nada, implementação) +
  duplicata; regras inegociáveis (mapa antes da poda, não reduzir cobertura de comportamento, git como
  evidência, suíte verde antes e depois); estados de evidência e veredito.
- `references/`: `taxonomia-do-que-podar.md`, `method.md`, `verification.md`, `git-as-evidence.md`.
- `templates/prune-log.md`: registro de poda (teste → família → ação → rede → commit).
- `evals/evals.json`: 6 cenários (podar passado, reescrever implementação, não podar comportamento sem
  rede, deletar duplicata + produção órfã, mapa antes de podar, veredito honesto). **`NOT_TESTED`** até
  execução registrada — ver `ROADMAP.md`.
- `scripts/validate_skill.py` + validadores comuns; entra no `quality-gate.py` e no CI.

### Proveniência
Registrada em `metadata` do `SKILL.md` e em `dados-design/VENDOR.md`. A 2ª skill de terceiro trazida
como skill-cidadã (depois da `untangle-codebase`, mesma origem Caldo). Scripts e fixtures da fonte não
foram trazidos; só a orientação, reescrita no formato do arsenal.
