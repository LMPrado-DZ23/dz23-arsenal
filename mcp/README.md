# dz23-subagents-universal-mcp

Servidor MCP (Model Context Protocol) para orquestração de sub-agentes e roteamento multi-modelo.

**Versão:** 4.4.1 · **Licença:** MIT · **Node:** 22+ · **Dependências de runtime:** nenhuma

## O que faz

Expõe ferramentas para delegar tarefas a diferentes modelos, rodar especialistas em paralelo, atingir
consenso entre revisores e persistir o estado de cada missão. Funciona com qualquer cliente MCP (Claude
Desktop, Cursor, DeepSeek Harness, Codex).

O princípio é "um projeto, vários modelos, uma memória compartilhada": a missão tem `project_id` e
`mission_id`, e o estado sobrevive à troca de modelo ou de harness.

## Instalação

```bash
cd mcp/dz23-subagents-universal-mcp
npm install       # se houver devDependencies; runtime é sem deps
```

## Configuração no cliente

```json
{
  "mcpServers": {
    "dz23-subagents": {
      "command": "node",
      "args": ["<path>/dz23-subagents-universal-mcp/src/index.js"]
    }
  }
}
```

## Ferramentas disponíveis

Extraídas do código-fonte (`src/`), não de documentação de intenção.

### Delegação e modelo

| Tool | O que faz |
|---|---|
| `delegate` | delega uma tarefa a um modelo, com papel e tipo de tarefa |
| `consensus` | 2–5 revisores independentes + síntese |
| `swarm_run` | até 7 especialistas em paralelo + revisor integrador |
| `list_models` | modelos configurados e elegíveis por política |
| `discover_models` | consulta catálogos dos provedores |
| `routing_explain` | mostra para onde a tarefa iria e por quê |
| `cost_estimate` | estimativa de custo antes de rodar |
| `verify_model` | prova de acesso a um modelo específico (billable) |
| `health_check` | geração mínima em cada alvo (billable) |
| `provider_inventory` | inventário de provedores configurados |
| `account_status` | status de login das CLIs de conta |

### Missão e memória

| Tool | O que faz |
|---|---|
| `mission_start` / `mission_status` / `mission_status_job` | ciclo de vida da missão |
| `mission_list` / `mission_cancel` / `mission_pause` / `mission_resume` | controle |
| `mission_claim` / `mission_release` | lease entre harnesses |
| `memory_checkpoint` | persiste estado estruturado para retomada |
| `handoff_export` | briefing para outro harness |
| `project_init` | metadados do projeto |
| `playbook_get` | playbooks de instrução |

### Código e workspace

| Tool | O que faz |
|---|---|
| `git_readonly` | leitura de repositório sem escrita |
| `audit_project` | auditoria de projeto |
| `review_pull_request` | revisão de PR |
| `patch_validate` | valida dry-run do patch |
| `workspace_read` / `workspace_search` | leitura e busca no workspace |

> A contagem do plano de montagem citava "28 tools". A extração do `src/` encontrou **31** nomes de tool.
> Documentei os 31 reais — a diferença é de contagem, não de função.

## Cuidados

- **Algumas tools são billable** (`verify_model`, `health_check`, `delegate`, `consensus`, `swarm_run`).
  Elas consomem crédito do provedor.
- Chaves de API ficam em variáveis de ambiente (`*_API_KEY`), nunca no repositório.
- `mission_start` cria job em background; use `mission_status_job` para acompanhar.
- Leases (`mission_claim`) coordenam harnesses cooperativos — não são autenticação.

## Versão e changelog

Ver `CHANGELOG.md` dentro desta pasta.
