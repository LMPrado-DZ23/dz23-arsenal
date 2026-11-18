# Compatibilidade — dz23-arsenal

## Sistemas operacionais

| Componente | Windows | Linux | macOS | Evidência |
|---|---|---|---|---|
| Instalador (`dz23-install.py`) | ✅ | ✅ | ✅ | Python stdlib; `install:autoteste` no gate |
| Quality gate | ✅ | ✅ | ✅* | CI roda em **Ubuntu + Windows** a cada push |
| `install-all.ps1` | ✅ | — | — | PowerShell |
| `install-all.sh` | — | ✅ | ✅ | bash |
| MCP (Node) | ✅ | ✅ | ✅* | `node:test`, 293 testes (subagents) |

`*` macOS não tem runner no CI — é suportado pelo código (Python/bash/Node portáveis), mas **não
exercitado** em CI; estado honesto: `NOT_TESTED` em macOS, `PASS` em Ubuntu e Windows.

O job Windows existe de propósito: o bug de encoding **cp1252** só se manifestava lá (gate
capturando subprocesso sem `encoding="utf-8"`). Ver `gate:autoteste-encoding-cp1252`.

## Runtimes

- **Python:** 3.10+ (obrigatório — instalador, gate, consultores). stdlib puro no runtime;
  `jsonschema` só no CI.
- **Node:** 20+ (apenas os MCP). `dz23-subagents-universal-mcp` tem **zero deps**; `pentagi-mcp`
  tem 3 deps diretas.

## Harnesses de agente

Skills descobertas em `~/.agents/skills` por **Claude Code, DeepSeek Harness, Codex e Cursor** (via
junction/symlink de `~/.claude/skills` e `~/.codex/skills`). O CLI `skills` (Vercel, catalogado)
instala para ~70 harnesses — adesão a esse padrão é item **ADAPTAR** em
[`matriz-de-requisitos.md`](matriz-de-requisitos.md).

## Ferramentas por skill (não garantidas)

Docker/kubectl (devops), Postgres (postgres-preflight), Playwright/browser (e2e), Ghidra/jadx/apktool
(reverse), Lighthouse/k6 (performance). Sem a ferramenta, a skill declara `BLOCKED`, não `PASS`.
Inventário real da máquina: [`cli/recommended.md`](cli/recommended.md). Limites:
[`LIMITATIONS.md`](LIMITATIONS.md).
