# Getting started — do zero ao primeiro uso

Cinco minutos, do clone ao primeiro comando funcionando.

## 1. Pré-requisitos mínimos

```bash
git --version      # qualquer versão recente
python --version   # 3.10+
node --version     # 20+
```

Se algum faltar, instale antes de continuar. `rg`, `jq` e `curl` são recomendados (várias skills os usam).

## 2. Clone

```bash
git clone https://github.com/LMPrado-DZ23/dz23-arsenal.git
cd dz23-arsenal
```

## 3. Instale as skills

**Windows (PowerShell):**
```powershell
.\scripts\install-all.ps1
```

**Linux / macOS:**
```bash
chmod +x scripts/install-all.sh
./scripts/install-all.sh
```

O instalador copia cada pasta de `skills/` para `~/.agents/skills/<nome>/`. Se a pasta já existir, ele
**não sobrescreve** — avisa `SKIP` e segue. Isso é de propósito: sobrescrever a skill instalada de alguém
sem perguntar é como um `rm -rf` educado.

## 4. Confira a instalação

```bash
python scripts/audit-zips.py    # integridade dos pacotes
pwsh scripts/verify-cli.ps1     # CLIs disponíveis e faltando
```

Saída esperada do `audit-zips.py`: uma linha por skill, com `EM_DIA` ou o detalhe da divergência.

## 5. Descubra as skills no seu agente

As skills são descobertas por convenção de diretório:

| Agente | Onde ele procura |
|---|---|
| Claude Code | `~/.claude/skills/` (costuma ser junction para `~/.agents/skills`) |
| DeepSeek Harness | `~/.agents/skills/` e `.dsh/profiles/*/` |
| Codex | `~/.codex/skills/` (junction para `~/.agents/skills`) |
| Cursor | `~/.cursor/skills/` ou MCP |

Se o seu agente não listar as skills, verifique se o caminho dele aponta para `~/.agents/skills`.

## 6. Primeiro uso

Cada skill tem um comando (quando `user-invocable: true`) e também ativa por descrição.

```bash
# Invocação explícita
/dz23-codebase-cartographer

# Ou por descrição — o agente carrega sozinho
"mapeia esse repositório antes de eu mexer"
```

## 7. Escolha a skill certa

Não sabe por onde começar? Use a tabela do [`skills/README.md`](../skills/README.md) — a coluna
"Se você quer…" resolve 90% dos casos.

## 8. Se algo der errado

| Sintoma | Causa provável | Solução |
|---|---|---|
| Comando não aparece | skill não instalada ou caminho errado | `ls ~/.agents/skills` |
| Skill carrega e falha em CLI | dependência da skill ausente | `cli/recommended.md` |
| `audit-zips.py` reporta divergência | zip e skill instalada diferem | reinstalar do repo |
| Agente ignora a skill | descrição não casa com o pedido | invoque pelo comando |

## Próximo passo

- Ler [`skills-overview.md`](skills-overview.md) para a tabela comparativa.
- Ler [`integration-map.md`](integration-map.md) para saber qual skill chama qual.
- Ler [`installing-skills.md`](installing-skills.md) se precisar de instalação manual ou por junction.
