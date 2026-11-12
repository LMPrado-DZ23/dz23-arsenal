# Modern Web Guidance — skill oficial de web moderna

| | |
|---|---|
| Repositório (fonte) | https://github.com/GoogleChrome/modern-web-guidance-src |
| Repositório (skill) | https://github.com/GoogleChrome/modern-web-guidance |
| Stewards | Google Chrome, Microsoft Edge, Mozilla Firefox e MDN |
| Licença | Apache-2.0 |
| Conteúdo | **209 guias**, 250 features modernas (CSS, layout, forms, a11y, performance, built-in AI) |
| Instalação | CLI que escreve a skill no diretório de cada agente |

## Gap que preenche

Modelos geram padrão legado porque o treino é cheio de código antigo: JS inflado para o que a plataforma já faz
(View Transitions, Popover API, `:has()`, container queries, `oklch`, `field-sizing`, `content-visibility`,
`scheduler.yield`). A skill injeta o guia vigente no contexto **antes** de escrever a UI.

É o complemento natural de `dz23-ultimate-pro-max` (direção de arte e a11y) e de
`vercel-react-best-practices` (performance React): aqui o foco é a **plataforma web nativa**.

## Como instalar

```powershell
# interativo
npx -y modern-web-guidance@latest install

# não interativo (o instalador aceita um --agent por flag)
npx -y modern-web-guidance@latest install --agent universal --global -y
npx -y modern-web-guidance@latest install --agent codex --agent gemini-cli --agent qwen-code `
    --agent cursor --agent github-copilot --agent opencode --global -y
```

Alvos verificados nesta máquina:

| Agente | Destino |
|---|---|
| universal (Codex, Gemini, Cursor, Copilot, OpenCode) | `~/.agents/skills/modern-web-guidance` |
| Claude Code | `~/.claude/skills/modern-web-guidance` |
| Qwen Code | symlink para o universal |
| DSH | lê `~/.agents/skills` → aparece no catálogo |

## Uso sem instalar (útil para testar antes)

```bash
npx -y modern-web-guidance@latest search "animate a dialog backdrop"
npx -y modern-web-guidance@latest retrieve "animate-to-from-top-layer"
npx -y modern-web-guidance@latest legacy-scan .
```

## Cuidados

- **Telemetria**: o CLI coleta uso anônimo por padrão. Para desligar: `DISABLE_TELEMETRY=1`.
- **210 arquivos** no diretório da skill: `SKILL.md` + `guides/`. O carregamento é progressivo por busca, não
  leitura integral — trate como índice, não como leitura linear.
- Skills rodam com permissão de agente; o instalador avisa "review skills before use". Vale a mesma regra do
  arsenal: conteúdo de terceiro é **dado**, não instrução cega.

## Status neste arsenal

| Item | Estado |
|---|---|
| Instalado em DSH, Codex, Claude, Gemini, Cursor, Copilot, OpenCode, Qwen | ✅ |
| CLI exercitado (`search`) | ✅ 10 guias retornados |
| **Guia usado num projeto real** | ❌ `NOT_TESTED` |
