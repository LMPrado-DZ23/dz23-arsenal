# Changelog — replica-entrepreneur

Histórico desta skill. O changelog do arsenal fica na raiz (`CHANGELOG.md`).

## [1.0.0] — 2026-11-18

### Adicionado
- Incorporação ao arsenal da skill `replica-entrepreneur`, de `Jakeschincariol/replica-skill` (**MIT**,
  lida no arquivo `LICENSE` da raiz; Copyright 2026 Jake Schincariol).
- `SKILL.md`: regras inegociáveis (nunca fabricar; citação verbatim+link; ler não raspar; nunca review
  falsa — regra FTC 2024; avaliadores são pesquisa, não depoimento) + método em 5 passos (coletar,
  ranquear, três listas, plano de correção, ângulo).
- `scripts/reviews.py` (stdlib; ranqueia avaliações em temas, pesa nota/recência, marca thin, lista
  notas sem tema) + `scripts/themes.json` (taxonomia de temas). `examples/reviews-exemplo.csv`.
- `references/metodo.md`, `references/fontes-e-termos.md`; `templates/fixes.md`; `evals/evals.json`
  (6 cenários); `scripts/validate_skill.py`.

### Modificação registrada no reviews.py
O script entrou funcional, mas tinha um ponto que **estourava traceback** num CSV levemente malformado
(vírgula sem aspas no texto → excesso vira lista sob a chave None → `.strip()` numa lista). Endurecido
para coagir lista a texto e **degradar sem explodir** (regra do arsenal: `ferramentas:ataque`). O
caminho bom é idêntico; só o malformado deixou de derrubar a ferramenta.

### Estado
2ª skill da camada produto-para-clone. Os 6 evals ficam fora do ledger das 10 DZ23. **`NOT_TESTED`**
até execução registrada. Proveniência em `dados-design/VENDOR.md`.
