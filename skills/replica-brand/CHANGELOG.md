# Changelog — replica-brand

Histórico desta skill. O changelog do arsenal fica na raiz (`CHANGELOG.md`).

## [1.0.0] — 2026-11-18

### Adicionado
- Incorporação ao arsenal da skill `replica-brand`, de `Jakeschincariol/replica-skill` (**MIT**, lida
  no arquivo `LICENSE` da raiz; Copyright 2026 Jake Schincariol).
- `SKILL.md`: regras inegociáveis (não confusamente similar; checagem rodada, não presumida; logo não
  pode parecer o do original; nome do original fora; triagem ≠ liberação jurídica) + método em 6 passos
  (nome, checagens, paleta, logo, voz, sweep).
- `scripts/sweep.py` (stdlib): acha nome/domínio/cor do original no conteúdo e nos nomes de arquivo
  (inclusive dentro de identificadores), exit 1 se achar — bloqueia deploy. `examples/brand-exemplo.json`.
- `references/checagens-legais.md`, `references/metodo.md`; `templates/brand.md`, `templates/brand.json`;
  `evals/evals.json` (6 cenários); `scripts/validate_skill.py`.

### Rerota (replica-design não incorporada)
O passo 3 (contraste) referenciava `../replica-design/contrast.py`. A `replica-design` ficou **fora**
do arsenal (duplicava `dz23-ultimate-pro-max` + o acervo de design). A checagem de contraste foi
**rerotada** para o acervo de acessibilidade (`web-design-guidelines`) ou `dz23-ultimate-pro-max`.

### Verificação
sweep.py entrou funcional, sem edição de comportamento, e é exercitado no gate
(`skills:scripts-executados`, 3 casos: código com sobra → exit 1, código limpo → exit 0, sem alvo → exit 2).

### Estado
4ª skill da camada produto-para-clone. Os 6 evals ficam fora do ledger das 10 DZ23. **`NOT_TESTED`**
até execução. Proveniência em `dados-design/VENDOR.md`.
