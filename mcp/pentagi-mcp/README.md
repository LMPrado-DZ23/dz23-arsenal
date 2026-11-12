# pentagi-mcp

Servidor **MCP** que expõe o [PentAGI](https://github.com/vxcontrol/pentagi) — plataforma de pentest autônomo self-hosted — para qualquer harness que fale o protocolo: **DSH, Claude Code, Codex, Gemini CLI, Qwen Code, OpenCode, Cursor, Copilot**.

O PentAGI não é MCP por si só: expõe REST + GraphQL com Bearer token (o MCP é recurso da edição Enterprise). Esta ponte resolve isso em 8 ferramentas, sem tocar no código do PentAGI.

## O que ele entrega

| Ferramenta | Para quê |
|---|---|
| `pentagi_status` | versão, providers configurados, nº de flows — rode antes das outras |
| `pentagi_list_flows` | lista flows (id, título, status, provider, datas) |
| `pentagi_get_flow` | detalhe de um flow com as tasks |
| `pentagi_create_flow` | cria um flow a partir de alvo + objetivo em linguagem natural |
| `pentagi_put_input` | envia instrução nova a um flow aguardando input |
| `pentagi_stop_flow` | para o flow mantendo histórico |
| `pentagi_finish_flow` | encerra como concluído |
| `pentagi_delete_flow` | **destrutivo**, exige `confirm: true` |

## Instalação

```powershell
# 1. PentAGI no ar (stack Docker)
cd D:\IA-Workspace\Deepseek\projects\pentagi
docker compose up -d          # https://127.0.0.1:8443

# 2. dependências da ponte
cd ..\pentagi-mcp
npm install

# 3. token (Settings → API Tokens no PentAGI) num arquivo
#    D:\IA-Workspace\Deepseek\projects\pentagi\api-token.txt

# 4. registrar nos harnesses (idempotente; faz backup manual antes)
pwsh -File install-harnesses.ps1

# 5. provar sem harness
node scripts/selftest.js
```

## Configuração (variáveis de ambiente)

| Variável | Default | Função |
|---|---|---|
| `PENTAGI_URL` | `https://127.0.0.1:8443` | base do PentAGI |
| `PENTAGI_TOKEN` | — | API token (JWT) inline |
| `PENTAGI_TOKEN_FILE` | — | arquivo com o token (preferido: segredo em um lugar só) |
| `PENTAGI_INSECURE` | ligado | aceita o certificado self-signed do stack local (`0` desliga) |

## Harnesses

| Harness | Onde foi registrado | Como valida |
|---|---|---|
| **DSH** | `D:\IA-Workspace\Deepseek\.dsh\profiles\desktop\cordis.patch.yml` (`mcp-pentagi`) | ferramentas `mcp__pentagi__*` na sessão |
| **Codex CLI** | `~/.codex/config.toml` (`[mcp_servers.pentagi]`) | `codex` → `/mcp` |
| **Claude Code** | `~/.claude.json` (`mcpServers.pentagi`) | `claude` → `/mcp` |
| Gemini CLI / Qwen Code / OpenCode / Cursor / Copilot | snippet em `harnesses-snippets.txt` | colar no config do harness |

O token **não** é copiado para os configs: todos apontam para `PENTAGI_TOKEN_FILE`.

## Estado verificado (2026-11-12)

| Item | Evidência |
|---|---|
| Stack PentAGI | 4 containers `Up`, `pgvector` healthy, migrações aplicadas, versão **2.2.0-ce.hcffed94** |
| API autenticada | `POST /auth/login` 200 · `GET /user/` 200 (privilégios) · `/settings/` 200 |
| Token de API | `POST /tokens/` **201** (JWT de 256 B, ttl 1 ano) |
| Ponte MCP | `node scripts/selftest.js` → **8 ferramentas, handshake ok, status e list_flows ok** |
| DSH | ferramentas `mcp__pentagi__*` visíveis e `pentagi_status` respondendo |

## O que NÃO está funcionando (declarado)

- **Nenhum provider de LLM configurado** → `pentagi_create_flow` não roda. O log do container mostra
  `failed to create embedder 'openai': missing the OpenAI API key`.
  Para habilitar: Settings → Providers no PentAGI (openai, anthropic, ollama, deepseek…), ou `.env` com
  `OPEN_AI_KEY`/`ANTHROPIC_API_KEY`/`LLM_SERVER_*` e `docker compose up -d pentagi`.
- **Nenhum flow executado** — logo, a capacidade de pentest em si é `NOT_TESTED`.
- **Gemini/Qwen/OpenCode/Cursor/Copilot** não estão instalados nesta máquina: receberam snippet, não registro.

## Segurança

PentAGI roda agentes que executam comandos em containers isolados e testam alvos. Use **apenas em alvo
autorizado**; o próprio README do projeto diz o mesmo. O token de API dá poder de admin neste banco —
trate `api-token.txt` como credencial.
