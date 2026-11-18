# OpenBot — workspace desktop para agentes persistentes

**Autor:** nightly-labs
**Repo:** https://github.com/nightly-labs/openbot
**Licença:** **PolyForm Noncommercial 1.0.0** — uso não comercial (ler antes de adotar em empresa)
**Site:** https://openbot.run
**Stack:** Electron + SolidJS + Bun (TypeScript), local-first
**Estado neste arsenal:** documentado, **não instalado nesta máquina** (`NOT_TESTED`)

## O que faz

Um app de desktop que dá a cada agente de código uma **equipe persistente**: workspace próprio, fila de
tarefas, conversa contínua, transferência de arquivos, browser embutido e mensagens entre agentes.

Roda os CLIs que o usuário já tem instalados, por **ACP**: Codex App Server, Claude Code, Grok CLI,
OpenCode, Gemini, Cursor CLI, Cline CLI, Kimi Code CLI, Devin CLI, GitHub Copilot CLI, Mistral Vibe e
Hermes Agent. Também aceita endpoint OpenAI-compatible e detecta servidores locais (Ollama, LM Studio).

| Recurso | Detalhe |
|---|---|
| Agentes persistentes | sessão própria por agente, com instruções, avatar e contexto independente |
| Fila FIFO | pausa, retoma, cancela; sobrevive a crash |
| Agente-a-agente | mensagens, respostas, reações, imagens, transferência de arquivo gerenciada |
| Canal compartilhado | um dono da tarefa, delegação explícita, histórico comum, reassinar/arquivar |
| Browser | embutido e persistente, que o agente abre, inspeciona e controla |
| Computer Use | opcional, via `cua-driver` (macOS, Windows, Linux) |
| Contexto | monitoramento por agente com compactação automática antes de estourar a janela |

## Por que usar em conjunto com DZ23

O arsenal resolve **delegação pontual**; o OpenBot resolve **equipe que continua viva**.

| Necessidade | Ferramenta certa |
|---|---|
| um subagente que responde uma pergunta e morre | `subagent_codex` / `subagent_claude_code` do DSH |
| delegação entre IAs com contexto e retorno | MCP `dz23-subagents` |
| agente A pedindo algo ao agente B, com fila e histórico | **OpenBot** |
| revisar código pelo terminal, com evidência | `ocr` (ver `skills-cli.md` e as skills DZ23) |

Não substitui o harness: ele **hospeda** os CLIs. O que ele adiciona é a camada de coordenação que hoje é
manual — fila, mensagem entre agentes e browser compartilhado.

## Instalação

```powershell
# opção 1 — release oficial (instalador por OS)
gh release list --repo nightly-labs/openbot --limit 3
gh release download --repo nightly-labs/openbot --pattern "*windows*" --dir .\openbot

# opção 2 — a partir da fonte (Bun)
git clone https://github.com/nightly-labs/openbot.git
cd openbot
bun install
bun run dev
```

## Cuidados — leia antes de instalar

1. **Licença noncommercial.** PolyForm Noncommercial 1.0.0 permite uso pessoal, pesquisa e avaliação; uso
   comercial exige licença à parte. Documentar isso é obrigação deste arsenal, não detalhe.
2. **Agentes rodam sem aprovação.** O README avisa: `danger-full-access` com `approvalPolicy: never` — leem e
   modificam arquivos, executam comandos, usam rede e controlam o browser sem confirmação por ação, depois do
   consentimento inicial. Rodar só com agente e tarefa em que se confia, com backup.
3. **Local-first.** Dados e sessões ficam na máquina; não há dependência de nuvem do projeto.
4. **Release quase diária.** Fixar versão em uso antes de depender do comportamento.

## O que este arsenal **não** afirma

- Não foi instalado nem exercitado nesta máquina: sem evidência de execução, fica `NOT_TESTED`.
- Não há benchmark do OpenBot contra o harness: os dois resolvem camadas diferentes.
- Números de popularidade não são publicados aqui (ver aviso em `external/README.md`).
