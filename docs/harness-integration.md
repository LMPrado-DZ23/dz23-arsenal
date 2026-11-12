# Integrar MCP e skills nos harnesses

O arsenal publica skills e servidores MCP. Cada harness descobre isso de um jeito diferente. Esta página é a
coluna vertebral comum — o que foi **verificado** nesta máquina e o que é receita para os demais.

## Matriz de descoberta

| Harness | Skills | MCP | Onde |
|---|---|---|---|
| **DSH** | `~/.agents/skills/<nome>/SKILL.md` | `dsh-mcp-client` no `cordis.patch.yml` do perfil | `D:\IA-Workspace\Deepseek\.dsh\profiles\desktop\cordis.patch.yml` |
| **Codex CLI** | `~/.agents/skills` (alvo universal) | `~/.codex/config.toml` → `[mcp_servers.<nome>]` | `~/.codex/` |
| **Claude Code** | `~/.claude/skills` + plugin/marketplace | `~/.claude.json` → `mcpServers` | `~/.claude*` |
| Gemini CLI · Qwen Code · OpenCode · Cursor · Copilot | diretórios próprios, ou `~/.agents/skills` via alvo universal | config próprio (`mcpServers` / `mcp`) | ver receitas abaixo |

**Convenção que funciona:** `~/.agents/skills` é o diretório que o instalador oficial do Modern Web Guidance
chama de `universal`. Quem publica skill para vários agentes deve apostar nele primeiro.

## Receitas de MCP (stdio)

### DSH — `cordis.patch.yml`

```yaml
- insert:
    - id: mcp-<nome>
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: <nome>
        transport: stdio
        command: node
        args: [ 'D:\caminho\server.js' ]
        env:
          VAR: 'valor'
        toolCallTimeoutMs: 300000
```

### Codex — `~/.codex/config.toml`

```toml
[mcp_servers.<nome>]
command = "node"
args = ["D:\\caminho\\server.js"]
startup_timeout_sec = 60

[mcp_servers.<nome>.env]
VAR = "valor"
```

### Claude Code — `~/.claude.json`

```json
{ "mcpServers": { "<nome>": { "type": "stdio", "command": "node",
  "args": ["D:\\caminho\\server.js"], "env": { "VAR": "valor" } } } }
```

### Gemini CLI · Qwen Code

```json
{ "mcpServers": { "<nome>": { "command": "node", "args": ["D:\\caminho\\server.js"],
  "env": { "VAR": "valor" } } } }
```

### OpenCode

```json
{ "mcp": { "<nome>": { "type": "local", "command": ["node", "D:\\caminho\\server.js"],
  "environment": { "VAR": "valor" }, "enabled": true } } }
```

### Cursor · Copilot CLI

Mesmo formato do Claude Code (`mcpServers`), em `~/.cursor/mcp.json` e `~/.copilot/mcp-config.json`.

## Cinco regras que evitam retrabalho

1. **Segredo em um lugar só.** O config aponta para `*_TOKEN_FILE`; o token não é copiado para três arquivos.
2. **Backup antes de editar config de harness.** `.bak.<timestamp>` custa nada e salva o dia.
3. **Não registre servidor que não pode responder.** Ferramenta que falha em toda chamada degrada o tool list
   de todos os harnesses — melhor deixar o script pronto e declarar `BLOCKED`.
4. **Certificado self-signed** é problema do cliente, não do servidor: `undici.Agent({ rejectUnauthorized:false })`
   ou `NODE_TLS_REJECT_UNAUTHORIZED` **no processo do MCP**, nunca global no shell.
5. **Valide com `selftest` antes de anunciar.** Handshake + `tools/list` + uma chamada real. Sem isso,
   "instalado" é só um arquivo de config.

## Scripts deste arsenal que fazem isso

| Script | O que registra |
|---|---|
| [`mcp/pentagi-mcp/install-harnesses.ps1`](../mcp/pentagi-mcp/install-harnesses.ps1) | MCP `pentagi` em DSH, Codex, Claude (e imprime snippets para os outros) |
| [`mcp/pentagi-mcp/scripts/selftest.js`](../mcp/pentagi-mcp/scripts/selftest.js) | handshake + ferramentas + chamada real |
| [`projects/pat-phone-agent-tool/install-pat-mcp.ps1`](https://github.com/azizdaurov/pat-phone-agent-tool) | MCP `pat-phone` (depende de hardware) |

## O que não é MCP

`modern-web-guidance` e `astryx` são **skills + CLI**, não servidores: o agente roda o comando
(`npx modern-web-guidance search …`, `astryx docs …`) e lê a saída. Registrar como MCP seria errado — o custo
seria um processo residente para servir o mesmo que um comando responde em 200 ms.
