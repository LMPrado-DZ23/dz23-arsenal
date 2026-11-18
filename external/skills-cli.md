# Skills CLI — o instalador de skills para agentes

**Autor:** vercel-labs
**Repo:** https://github.com/vercel-labs/skills
**Licença:** MIT
**Versão verificada:** `skills` 1.9.0 (npm), instalado e exercitado em 2026-11-18

## O que faz

Não é uma skill: é o **gerenciador** de skills de agentes. Um comando `skills` que instala, atualiza, lista
e remove skills a partir de um repositório git, uma URL ou uma pasta local — gravando nos diretórios que
cada harness realmente lê (`~/.agents/skills`, `~/.claude/skills`, `~/.codex/skills`, `~/.config/opencode/...`
e mais ~70 agentes mapeados em `src/agents.ts`).

O detalhe que importa: ele **sabe** onde cada agente procura. `~/.agents/skills` é o diretório neutro lido
por DSH, Codex, OpenCode, Cline e Cursor; os demais recebem link ou cópia no caminho próprio.

| Comando | Para quê |
|---|---|
| `skills add <owner>/<repo>` | instala o pacote inteiro ou `--skill <nome>` |
| `skills find "pdf"` | busca no ecossistema antes de instalar |
| `skills list -g` | o que está instalado, de que origem, e **quem lê** |
| `skills check` | compara hash de pasta com o GitHub e diz o que tem update |
| `skills update` | reinstala só o que mudou |
| `skills remove <skill>` | desinstala |
| `skills init <nome>` | cria o esqueleto de `SKILL.md` |

## Por que usar em conjunto com DZ23

| Necessidade | Sem o CLI | Com o CLI |
|---|---|---|
| descobrir se já existe skill para o problema | garimpar GitHub | `skills find "video"` |
| instalar em 5 harnesses | copiar 5 vezes, à mão | um comando, `-a universal -a claude-code -a codex ...` |
| saber o que está velho | comparar repositório por repositório | `skills check` |
| remover sem deixar lixo | apagar pasta e torcer | `skills remove <nome>` |

As 10 skills DZ23 continuam sendo instaladas por `scripts/install-all.ps1`; o CLI é para as **externas**
documentadas em `external/`.

## Instalação

```powershell
npm install -g skills
skills --version     # 1.9.0 nesta máquina

# instalar em todos os agentes presentes, sem prompt
npx skills add caldoai/skills -g -y -a universal -a claude-code -a codex -a opencode `
  -a aider-desk -a cline -a cursor -a grok -a hermes-agent
```

`-g` = escopo global (usuário). Sem `-g`, instala no projeto atual, em `.agents/skills`.

## Uso

```powershell
skills list -g          # inventário com origem e agentes
skills find "react"     # busca
skills check            # exit 1 quando há atualização pendente
skills update           # aplica
```

## Cuidados

- **Skill roda com as permissões do agente.** O próprio CLI avisa: *"Review skills before use; they run with
  full agent permissions."* Não instale o que não leu.
- **`check`/`update` só enxergam o lock.** O arquivo `~/.agents/.skill-lock.json` (formato v3) guarda
  `skillFolderHash` por skill. Nesta máquina há **19** skills rastreadas e **~120** instaladas fora do lock —
  essas aparecem como `untracked` e nunca recebem update automático.
- **A skill é markdown; o binário é outra trilha.** Atualizar `agent-desktop` (skill) não atualiza o pacote
  npm `agent-desktop` (1.2.0 → 1.3.1 no npm, medido nesta máquina).
- **Ferramentas de terceiros mudam.** O `check` compara hash de pasta, não semântica: um update pode trocar
  instruções do `SKILL.md`. Ler o diff antes de aplicar em skill que você usa todo dia.
