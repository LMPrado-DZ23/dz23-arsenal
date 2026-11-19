# Paperclip — orquestração de equipe de agentes como se fosse uma empresa

**Autor:** paperclipai
**Repo:** https://github.com/paperclipai/paperclip
**Licença:** MIT (confirmada via API do GitHub: `license.spdx_id = MIT`)
**Docs:** https://docs.paperclip.ing · **Site:** https://paperclip.ing
**Stack:** Node.js (servidor) + React (UI) · TypeScript
**Estado nesta máquina:** **instalado e rodando** em 2026-11-19 — dashboard `http://127.0.0.1:3100`

## O que faz

Um servidor Node com UI React que orquestra **um time de agentes** como se fosse uma empresa: organograma,
cargos, metas, orçamento, governança e histórico de trabalho num só painel. Cada agente pode usar modelo e
harness próprios (Claude Code, Codex, OpenCode, Hermes, ACP…).

A frase do próprio projeto explica o posicionamento: *"If OpenClaw is an employee, Paperclip is the company."*

| Peça | O que é |
|---|---|
| Organograma | agentes com papel, título e linha de reporte |
| Metas | objetivo de negócio ("chegar a US$ 1M de MRR"), não fila de PRs |
| Orçamento | limite de gasto por agente, com relatório de uso |
| Governança | permissões, aprovações e trilha de auditoria |
| Portabilidade | exportar/importar empresa inteira — orgs, agentes e skills |

## Por que usar junto do arsenal

O arsenal entrega **método e ferramenta** (skills, prompts, MCPs). O Paperclip entrega a camada que hoje só
existe em planilha: quem faz o quê, com que orçamento, sob qual meta.

| Necessidade | Ferramenta |
|---|---|
| avaliar código com evidência | `ocr` (ver `external/skills-cli.md`) |
| delegar tarefa a outro agente | MCP `dz23-subagents` |
| agentes persistentes com fila e browser | OpenBot (ver `external/openbot.md`) |
| **time inteiro com metas, cargos e orçamento** | **Paperclip** |

## Instalação — o que funcionou (e o que não)

Requisito: **Node.js ≥ 24.11** (aqui: v26.13.0).

### `paperclipai install` falha no Windows

```
$ npx paperclipai@latest install -y
Resolving paperclipai@latest from npmjs.org...
spawn npm ENOENT
```

O instalador gerenciado chama `npm` direto (`spawn('npm')`), e no Windows o comando é `npm.cmd` — precisa de
shell. **Bug do instalador, não da máquina.** Caminho alternativo que funciona:

```powershell
# 1. instalar o pacote direto (equivale ao store gerenciado)
npm install -g paperclipai@latest

# 2. permitir os install scripts: sem eles o Postgres embarcado e os assets não são baixados
npm install -g paperclipai@latest --allow-scripts=@embedded-postgres/windows-x64,opencode-ai,ssh2,protobufjs,@paperclipai/server

# 3. conferir
paperclipai --version     # 2026.1117.0
```

### Habilitar a instância

```powershell
paperclipai onboard --yes --bind loopback --no-install-service
```

`--bind loopback` deixa o painel acessível só na máquina. `--no-install-service` porque **serviço de fundo não
é suportado no Windows** (o próprio `doctor` informa: *"Service management is not supported on win32. Use
`paperclipai run` instead."*).

Resultado em `~/.paperclip/instances/default/`:

| Item | Valor medido |
|---|---|
| Dashboard | `http://127.0.0.1:3100` (HTTP 200) |
| Banco | **Postgres embarcado** na porta `54329`, dados em `db/` |
| Segredos | `secrets/master.key` (criptografia local) |
| Backup | habilitado, a cada 60 min, retenção 30 dias |
| Exposição | `private` / `loopback` — sem hostname público |
| Doctor | **11 passed, 1 warning** (warning = porta 3100 em uso pela própria instância) |

## Uso

```powershell
paperclipai run            # sobe a instância (Windows: é o caminho, não há serviço)
paperclipai doctor         # diagnósticos
paperclipai db:backup      # backup pontual
paperclipai update         # atualiza a CLI, com rollback
```

O painel abre em `http://127.0.0.1:3100`.

## Onde a instalação parou — e por que

O onboarding do painel tem 5 passos: organização → primeiro agente → **conectar modelo** → … → pronto.
Cheguei ao passo 3 (`Connect a model`), que oferece assinatura ou **API key** de Claude/OpenAI.

Parei de propósito: colar uma chave de modelo é decisão do dono, e chave de API não é coisa que um agente
preenche por conta própria num formulário. A instância está pronta para retomar em
`http://127.0.0.1:3100/onboarding`.

Estado real: **servidor instalado e respondendo** (`INSTALADO`), orquestração de agentes **não exercitada**
(`NOT_TESTED`) — depende de conectar modelo no painel.

## Cuidados

- **Superfície de risco alta**: é um servidor que coordena agentes com autonomia. Rodar em `loopback` até
  entender as permissões; mudar para `lan`/`tailnet` só com TLS e autenticação.
- **Postgres embarcado**: os dados ficam em `~/.paperclip/instances/default/db`. Backup antes de qualquer
  update — o `db:backup` existe para isso.
- **Telemetria ligada por padrão** (`telemetry.enabled: true` no `config.json`). Desligar em `configure` se
  não quiser enviar uso.
- **Nunca coloque a chave de modelo em arquivo versionado.** O Paperclip guarda em `secrets/` criptografado;
  mantenha assim.
