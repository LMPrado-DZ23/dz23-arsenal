# Changelog — replica-diff

Histórico desta skill. O changelog do arsenal fica na raiz (`CHANGELOG.md`).

## [1.0.0] — 2026-11-18

### Adicionado
- Incorporação ao arsenal da skill `replica-diff`, de `Jakeschincariol/replica-skill` (**MIT**, lida
  no arquivo `LICENSE` da raiz; Copyright 2026 Jake Schincariol).
- `SKILL.md`: paridade é fazer o mesmo trabalho, não parecer igual; método em 4 passos (features,
  layout, comportamento, relatório); veredito (não shippable / shippable / melhor que o original).
- `scripts/parity.py` (stdlib): score de paridade de features da matriz, pesado por prioridade, com a
  lista do que falta em ordem de construção; `--visual`, `--markdown`, `--fail-under`.
- `scripts/imgdiff.py` (stdlib, decoder PNG próprio): diff de layout por screenshot que **ignora cor**
  (edge map em grade), modo pixel para regressões próprias.
- `references/o-que-e-paridade.md`, `references/metodo.md`; `templates/parity.md`;
  `examples/features-exemplo.csv`, `examples/orig.png`, `examples/clone.png`; `evals/evals.json`
  (6 cenários); `scripts/validate_skill.py`.

### Verificação
Ambos os scripts entraram funcionais e são exercitados no gate (`skills:scripts-executados`): parity.py
contra a matriz de exemplo (+ controle negativo sem coluna) e imgdiff.py contra os dois PNGs de
exemplo. Nenhuma edição de comportamento foi necessária.

### Estado
3ª skill da camada produto-para-clone. Os 6 evals ficam fora do ledger das 10 DZ23. **`NOT_TESTED`**
até execução registrada. Proveniência em `dados-design/VENDOR.md`.
