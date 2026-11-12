# PentAGI — plataforma de pentest autônomo self-hosted

| | |
|---|---|
| Repositório | https://github.com/vxcontrol/pentagi |
| Autor | [VXControl](https://vxcontrol.com) |
| Licença | LICENSE do próprio repo + [`EULA.md`](https://github.com/vxcontrol/pentagi/blob/main/EULA.md) |
| Stack | Go (REST + GraphQL) · React · PostgreSQL + pgvector · Docker Compose |
| O que é | multi-agente autônomo de **pentest**: planeja, executa 20+ ferramentas (nmap, Metasploit, sqlmap) em sandbox Docker, memoriza (pgvector) e entrega relatório |
| O que **não** é | não é servidor MCP na edição open source — MCP é recurso da **Enterprise** |

## Gap que preenche

Nenhuma skill DZ23 executa pentest. `security-review` revisa código, `dz23-reverse-engineer-anything` analisa
binário, `dz23-postgres-prod-preflight` audita banco — todas param antes de "atacar o alvo". PentAGI é a camada
que executa o ataque (com autorização) e devolve relatório.

## Como instalar (Windows/Linux/macOS)

```bash
git clone https://github.com/vxcontrol/pentagi.git
cd pentagi
cp .env.example .env
# mínimo: um provider de LLM (OPEN_AI_KEY, ANTHROPIC_API_KEY, LLM_SERVER_* ou OLLAMA_SERVER_*)
# e um salt real, senão a criação de API token é recusada:
#   COOKIE_SIGNING_SALT=<32 hex>
docker compose up -d          # https://127.0.0.1:8443
```

O primeiro usuário é criado pela UI (o endpoint `POST /users/` exige auth). Sem provider de LLM o stack sobe e
autentica, mas `createFlow` falha e o log mostra
`failed to create embedder 'openai': missing the OpenAI API key`.

## Como o arsenal usa

O PentAGI não fala MCP no OSS, então este repositório traz a ponte [`mcp/pentagi-mcp`](../mcp/pentagi-mcp):
um servidor MCP stdio com **8 ferramentas** sobre a API GraphQL (`status`, `list_flows`, `get_flow`,
`create_flow`, `put_input`, `stop_flow`, `finish_flow`, `delete_flow`).

```bash
node mcp/pentagi-mcp/scripts/selftest.js   # handshake + tools/list + status + list_flows
```

Registro por harness: ver [`docs/harness-integration.md`](../docs/harness-integration.md).

## Cuidados

- **Só alvo autorizado.** O projeto é para pentest autorizado; o próprio README diz isso.
- **Peso**: imagens ~22 GB (`pentagi` 889 MB, `scraper` 4,68 GB, `pgvector` 614 MB), volumes ~6 GB.
- **Token de API = admin** do banco. Guarde em arquivo com permissão restrita; não cole em chat nem em log.
- Porta padrão **8443 com TLS self-signed** — cliente precisa aceitar o certificado (na ponte: `PENTAGI_INSECURE`).
- Roda sandbox Docker por flow: exige Docker acessível ao container (`PENTAGI_DOCKER_SOCKET`).

## Status neste arsenal

| Item | Estado |
|---|---|
| Stack instalado e autenticando | ✅ 4 containers, versão `2.2.0-ce` |
| Ponte MCP | ✅ 8 ferramentas, selftest sem falha |
| Registro em DSH/Codex/Claude | ✅ |
| **Executar um flow** | ❌ `BLOCKED_BY_EXTERNAL_DEPENDENCY` — falta provider de LLM |
