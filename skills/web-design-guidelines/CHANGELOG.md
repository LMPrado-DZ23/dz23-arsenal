# Changelog — web-design-guidelines

Histórico desta skill. O changelog do arsenal fica na raiz (`CHANGELOG.md`).

## [1.0.0] — 2026-11-18

### Adicionado
- Incorporação ao arsenal: revisão de UI contra as **Web Interface Guidelines**, com o conhecimento
  **internalizado** (offline, sem WebFetch).
- `dados/regras-por-categoria.csv`: **104 regras em 17 categorias**, extraídas de `command.md` de
  `vercel-labs/web-interface-guidelines` (**MIT**, lida no `LICENSE` da raiz; Copyright 2025 Vercel Labs,
  confirmada via API do GitHub). `references/web-interface-guidelines.md` guarda o documento completo.
- `scripts/consulta-web.py`: consulta por categoria em português (mapa fechado de sinônimos, palavra
  inteira, "sem correspondência" quando não há) + `busca` no texto das regras. Prova em
  `scripts/prova-consulta-web.py` (categorias certas, 3 controles negativos, sinônimos vivos, esquema).
- `templates/relatorio-revisao.md`, `evals/evals.json` (6 cenários), `scripts/validate_skill.py`.
- `SKILL.md` com fluxo de revisão, acervo consultável, regras inegociáveis (achado cita regra do
  acervo; não altera código; `arquivo:linha` real; offline) e veredito.

### Decisão de incorporação
A skill `web-design-guidelines` de `vercel-labs/agent-skills` **não** foi usada: sem licença
(`license:null`, sem `LICENSE`) e dependia de WebFetch remoto. Trazido o conhecimento real
(`web-interface-guidelines`, MIT). Proveniência em `dados/PROVENIENCIA.md` e `dados-design/VENDOR.md`.

### Estado
Os 6 evals ficam **fora** do ledger "144 cenários" das 10 DZ23. **`NOT_TESTED`** até execução
registrada — ver `ROADMAP.md`.
