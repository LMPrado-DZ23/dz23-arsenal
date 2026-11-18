# Changelog — replica-recon

Histórico desta skill. O changelog do arsenal fica na raiz (`CHANGELOG.md`).

## [1.0.0] — 2026-11-18

### Adicionado
- Incorporação ao arsenal da skill `replica-recon`, de `Jakeschincariol/replica-skill` (**MIT**, lida
  no arquivo `LICENSE` da raiz; Copyright 2026 Jake Schincariol). Conteúdo internalizado e adaptado em
  português ao rito do arsenal, não copiado byte a byte.
- `SKILL.md`: regras de clean-room inegociáveis (fontes públicas + conta do próprio usuário; ler, não
  raspar; sem código-fonte/API privada; conferir termos; screenshots só como referência) + método em
  9 passos (escopo, fontes, telas, fluxos, componentes, modelo de dados, matriz, fora-de-escopo,
  tamanho) + entregáveis e veredito.
- `references/`: `clean-room.md`, `metodo.md`, `fontes.md`.
- `templates/`: `recon-map.md` (mapa) e `features.csv` (matriz).
- `evals/evals.json`: 6 cenários (recusa login alheio, não lê código-fonte, escopa a fatia, estados
  por tela, evidência+chute, fora-de-escopo honesto). **`NOT_TESTED`** até execução — ver `ROADMAP.md`.
- `scripts/validate_skill.py` + validadores comuns; entra no `quality-gate.py` e no CI.

### Papel no arsenal
Primeira skill da camada **produto-para-clone**. Não colide com `dz23-reverse-engineer-anything`
(binário/firmware): esta é recon black-box de produto. Proveniência em `dados-design/VENDOR.md`; os 6
evals ficam fora do ledger das 10 DZ23.
