# Proveniência — dados/regras-por-categoria.csv

- **Fonte:** `vercel-labs/web-interface-guidelines`, arquivo `command.md`.
- **Licença:** **MIT**, lida no arquivo `LICENSE` da raiz do repositório de origem (Copyright 2025
  Vercel Labs) — confirmada via API do GitHub (`spdx_id: MIT`, arquivo `LICENSE` presente).
- **O que é:** 104 regras de interface web em 17 categorias (Accessibility, Focus States, Forms,
  Animation, Typography, Content Handling, Images, Performance, Navigation & State, Touch & Interaction,
  Safe Areas & Layout, Dark Mode & Theming, Locale & i18n, Hydration Safety, Hover & Interactive States,
  Content & Copy, Anti-patterns). Cada linha: `categoria`, `regra`, `origem_arquivo`, `origem_secao`.
- **Como foi gerado:** extração das listas de `command.md` (bullets sob cada `###`), sem edição do
  texto das regras. A reference `references/web-interface-guidelines.md` guarda o documento completo.
- **Por que internalizar (e não a skill da Vercel):** a skill `web-design-guidelines` de
  `vercel-labs/agent-skills` **não tem licença** (API do GitHub devolve `license:null`, sem arquivo
  `LICENSE`) e **busca as regras de uma URL remota a cada uso** — não se redistribui, e feriria a
  autonomia. O conhecimento real (`web-interface-guidelines`) é MIT e foi trazido para dentro: a skill
  revisa offline, sem WebFetch.
- **Verificação:** `scripts/prova-consulta-web.py` exige categorias certas, 3 controles negativos
  (recusa honesta), todos os sinônimos PT apontando para categoria existente, esquema e contagem.
