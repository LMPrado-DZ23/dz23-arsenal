# Astryx — design system da Meta, feito para gente e agentes

| | |
|---|---|
| Repositório | https://github.com/meta/astryx |
| Autor | Meta (open source) |
| Licença | MIT |
| Base | React 19+ · StyleX (invisível ao consumidor) |
| Conteúdo | 150+ componentes acessíveis, 7 temas, templates, CLI (`@astryxdesign/cli`) |
| Docs | https://astryx.atmeta.com |
| Estado | **Beta** |

## Gap que preenche

`dz23-ultimate-pro-max` define direção de arte, estados e a11y **sem** impor biblioteca. O Astryx é o oposto
complementar: uma biblioteca pronta, com API estável e CLI que **o agente consulta** (`astryx component Button`,
`astryx docs guides/...`) em vez de ler o código-fonte do pacote.

Para um app React 19 que precisa sair rápido e consistente, é a rota de menor atrito.

## Como instalar

```powershell
# CLI global: fica disponível em qualquer pasta, para qualquer agente
npm i -g @astryxdesign/cli        # 0.7.14 nesta máquina
astryx --version
astryx docs guides                # docs que o agente deve ler, não o código do pacote
astryx search "data table"
```

```bash
# num projeto React 19
npm install @astryxdesign/core @astryxdesign/theme-neutral @stylexjs/stylex
npm install -D @astryxdesign/cli
npx astryx init
```

A skill portátil que ensina o agente a usar o CLI está em `plugins/astryx/skills/astryx/SKILL.md` no repo
oficial. Este arsenal a instala em `~/.agents/skills/astryx` (lida por DSH, Codex, Claude, Gemini, Cursor…),
com os plugins oficiais preservados em `~/.agents/skills/astryx/_oficial/`:

| Plugin oficial | Arquivo | Para |
|---|---|---|
| Claude Code | `.claude-plugin/plugin.json` | marketplace de plugin do Claude |
| Codex | `.codex-plugin/plugin.json` | plugin do Codex |

Instale o plugin pela CLI do respectivo harness quando ela estiver no PATH; a skill em `~/.agents/skills/astryx`
já cobre o uso por CLI em qualquer agente.

## Cuidados

- **Beta** — API pode mudar; o CLI avisa a versão do Core que respondeu.
- Exige **React 19+**; não é drop-in em React 18.
- `astryx` fora de um projeto usa a versão global; dentro de um projeto, a versão do projeto responde primeiro.
- Skill de terceiro: leia antes de deixar um agente executar `astryx init` (ele escreve arquivos no projeto).

## Status neste arsenal

| Item | Estado |
|---|---|
| CLI global | ✅ `astryx 0.7.14` |
| Skill em `~/.agents/skills/astryx` | ✅ (frontmatter + plugins oficiais) |
| Catálogo do DSH | ✅ aparece como `astryx` |
| **Componente renderizado num app React 19** | ❌ `NOT_TESTED` |
