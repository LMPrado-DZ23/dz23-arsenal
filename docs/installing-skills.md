# Instalando skills DZ23

Três caminhos: instalador, manual, e junction. Escolha conforme o caso.

## Caminho 1 — instalador (recomendado)

```powershell
# Windows
.\scripts\install-all.ps1
```

```bash
# Linux / macOS
./scripts/install-all.sh
```

O script copia `skills/<nome>/` → `~/.agents/skills/<nome>/` e **não sobrescreve** o que já existe.

## Caminho 2 — manual (uma skill)

```bash
# Windows
xcopy skills\dz23-devops-cloud-deployer "%USERPROFILE%\.agents\skills\dz23-devops-cloud-deployer\" /E /I

# Linux / macOS
cp -r skills/dz23-devops-cloud-deployer ~/.agents/skills/dz23-devops-cloud-deployer
```

## Caminho 3 — junction / symlink (para desenvolvimento)

Útil quando você quer editar a skill no repo e ver o efeito na hora, sem copiar de novo.

**Windows (precisa de Developer Mode ou terminal como admin):**
```powershell
New-Item -ItemType Junction `
  -Path "$env:USERPROFILE\.agents\skills\dz23-devops-cloud-deployer" `
  -Target "D:\IA-Workspace\dz23-arsenal\skills\dz23-devops-cloud-deployer"
```

**Linux / macOS:**
```bash
ln -s "$(pwd)/skills/dz23-devops-cloud-deployer" ~/.agents/skills/dz23-devops-cloud-deployer
```

> **Atenção:** no Windows, `New-Item -ItemType SymbolicLink` exige privilégio de administrador, mesmo com
> Developer Mode em algumas versões. `Junction` funciona para diretórios e exige menos. Se ambos
> falharem, use a cópia (caminho 1 ou 2) — não perca tempo brigando com o sistema de arquivos.

**Linux / macOS com junction equivalente para o agente:**
```bash
ln -s ~/.agents/skills ~/.claude/skills    # Claude Code
ln -s ~/.agents/skills ~/.codex/skills     # Codex
```

## Onde cada agente procura

| Agente | Caminho padrão | Observação |
|---|---|---|
| DeepSeek Harness | `~/.agents/skills/` e `.dsh/profiles/*/` | lê o diretório direto |
| Claude Code | `~/.claude/skills/` | normalmente junction para `~/.agents/skills` |
| Codex | `~/.codex/skills/` | idem |
| Cursor | `~/.cursor/skills/` | suporta subdiretórios |

## Verificar se foi instalada

```bash
# lista as skills
ls ~/.agents/skills

# confere o frontmatter de uma
head -5 ~/.agents/skills/dz23-reverse-engineer-anything/SKILL.md
```

Saída esperada: frontmatter com `name`, `version`, `description`, `user-invocable`.

## Atualizar uma skill

```bash
cd dz23-arsenal
git pull
rm -rf ~/.agents/skills/<nome>
./scripts/install-all.sh    # reinstala só o que falta
```

Ou manualmente, copiando por cima. **Sempre apague antes de copiar** se a versão nova removeu arquivos —
`cp -r` não remove o que sobrou da versão antiga.

## Desinstalar

```bash
rm -rf ~/.agents/skills/<nome>
```

## Problemas comuns

| Sintoma | Causa | Solução |
|---|---|---|
| `Permission denied` no symlink | Windows sem privilégio | usar Junction ou copiar |
| Skill aparece duplicada | instalada em dois caminhos | remover a cópia antiga |
| Agente não vê a skill nova | cache do agente | reiniciar a sessão do agente |
| `SKIP` no instalador | pasta já existia | remover e rodar de novo |
| Frontmatter inválido | cópia parcial/sem permissão | verificar `SKILL.md` e copiar de novo |
