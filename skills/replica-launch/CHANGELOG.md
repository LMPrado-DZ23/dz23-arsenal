# Changelog — replica-launch

Histórico desta skill. O changelog do arsenal fica na raiz (`CHANGELOG.md`).

## [1.0.0] — 2026-11-18

### Adicionado
- Incorporação ao arsenal da skill `replica-launch`, de `Jakeschincariol/replica-skill` (**MIT**, lida
  no arquivo `LICENSE` da raiz; Copyright 2026 Jake Schincariol). Última da camada produto-para-clone.
- `SKILL.md`: regras (sem prova falsa; avaliações não são depoimento; nome do original fora da
  listagem) + método em 4 passos (landing, preço, listagem, plano).
- `scripts/listing.py` (stdlib): lint da listagem contra os limites de App Store/Google Play e as regras
  anti-cópia (nome do original em qualquer campo, claims de ranking/preço, emoji, keywords
  desperdiçadas), exit 1 em erro. `examples/listing-exemplo.json`.
- `references/metodo.md`, `references/lojas.md` (limites + Guideline 4.1 Copycats da Apple);
  `templates/landing.md`, `pricing.md`, `launch-plan.md`; `evals/evals.json` (6 cenários);
  `scripts/validate_skill.py`.

### Rerota (replica-design não incorporada)
O contraste da landing referenciava `replica-design`; rerotado para `web-design-guidelines`/
`dz23-ultimate-pro-max`.

### Verificação
listing.py entrou funcional, sem edição, exercitado no gate (`skills:scripts-executados`, 3 casos:
exemplo → exit 0, nome do original presente → exit 1, JSON inválido → exit 2).

### Estado
5ª e última skill da camada produto-para-clone — a suíte replica (recon/entrepreneur/diff/brand/launch)
está completa. Os 6 evals ficam fora do ledger das 10 DZ23. **`NOT_TESTED`** até execução. Proveniência
em `dados-design/VENDOR.md`.
