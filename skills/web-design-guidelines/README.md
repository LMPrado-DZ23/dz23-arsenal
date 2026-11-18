# web-design-guidelines

Revisa código de UI contra as **Web Interface Guidelines** — 104 regras em 17 categorias
(acessibilidade, foco, formulários, animação, tipografia, performance, dark mode, i18n, hidratação,
anti-padrões e mais). O conhecimento vive **dentro** da skill: revisa offline, sem buscar de URL
remota, sem depender de terceiro a cada uso. Saída concisa em `arquivo:linha`.

Use ao pedir "revise minha UI", "audite acessibilidade", "cheque contra boas práticas", antes de abrir
PR de frontend, ou junto da `dz23-ultimate-pro-max` (que desenha a UI; esta confere a UI pronta). Não é
lint de estilo nem reescrita — é auditoria de conformidade que reporta achados.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| [`SKILL.md`](SKILL.md) | As regras: como revisar, acervo consultável, regras inegociáveis, veredito |
| [`dados/regras-por-categoria.csv`](dados/regras-por-categoria.csv) | 104 regras, cada uma com categoria e seção de origem |
| [`references/web-interface-guidelines.md`](references/web-interface-guidelines.md) | O documento completo das guidelines (cópia fiel, MIT) |
| [`templates/relatorio-revisao.md`](templates/relatorio-revisao.md) | Modelo de relatório em `arquivo:linha` |
| [`evals/evals.json`](evals/evals.json) | 6 cenários de avaliação |

Consulta: `python scripts/consulta-web.py listar` · `... categoria acessibilidade` · `... busca aria`.

## Por que não a skill da Vercel diretamente

A skill `web-design-guidelines` de `vercel-labs/agent-skills` **não tem licença** (API do GitHub devolve
`license:null`, sem arquivo `LICENSE`) e **busca as regras de uma URL remota** a cada uso. O arsenal não
redistribui conteúdo sem licença e preza autonomia, então internalizou o **conhecimento real** —
`vercel-labs/web-interface-guidelines` (**MIT**, com `LICENSE`) — que a skill agora carrega offline.

## Arsenal

Esta skill faz parte do [dz23-arsenal](../../README.md). **Origem das regras:**
[`vercel-labs/web-interface-guidelines`](https://github.com/vercel-labs/web-interface-guidelines)
(`command.md`), licença **MIT** lida no arquivo `LICENSE` da raiz (Copyright 2025 Vercel Labs).
Internalizado e adaptado ao rito do arsenal (acervo, consultor, eval, gate) — ver `metadata` no
[`SKILL.md`](SKILL.md) e o registro em [`dados-design/VENDOR.md`](../../dados-design/VENDOR.md).

Instalação e índice geral: [`README.md`](../../README.md). Estado de evals: [`ROADMAP.md`](../../ROADMAP.md).
