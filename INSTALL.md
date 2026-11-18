# Instalação — dz23-arsenal

Guia canônico de instalação. Detalhe do instalador: [`install/README.md`](install/README.md).
Dependências de CLI por skill: [`cli/required.md`](cli/required.md).

## Caminho rápido

```bash
git clone https://github.com/LMPrado-DZ23/dz23-arsenal.git
cd dz23-arsenal

# Instalador multiplataforma (Windows/Linux/macOS) — offline, com rollback
python scripts/dz23-install.py detect        # dependências AVAILABLE/UNAVAILABLE
python scripts/dz23-install.py install --dry-run   # simula, não muda nada
python scripts/dz23-install.py install       # copia as 18 skills para ~/.agents/skills
python scripts/dz23-install.py rollback      # desfaz (remove só o que o manifesto registra)
```

Caminho simples alternativo (scripts dedicados): `.\scripts\install-all.ps1` (Windows) ou
`./scripts/install-all.sh` (Linux/macOS).

## Onde as skills ficam

`~/.agents/skills/<nome>/` — descobertas por Claude Code, DeepSeek Harness, Codex e Cursor (via
junction/symlink de `~/.claude/skills` e `~/.codex/skills`). O ponteiro `.dz23-arsenal` aponta de
volta ao checkout.

## Garantias (verificadas no gate: `install:autoteste`)

Detecção de dependências · dry-run inócuo · **offline** (só cópia, nenhuma rede) · manifesto +
**rollback preciso** · idempotência · **log sem segredos** · sem bytecode no destino. Ver
[`install/README.md`](install/README.md) para a tabela completa.

## Pré-requisitos

- **Obrigatório:** `python` 3.10+ (roda o instalador e o gate).
- **Base recomendada:** `git`, `node` 20+ (MCP), `rg`, `jq`, `curl`.
- **Por skill:** [`cli/required.md`](cli/required.md) (docker/kubectl para devops, playwright para
  e2e, Ghidra para reverse, etc.). O que falta nesta máquina: [`cli/recommended.md`](cli/recommended.md).

## Verificação pós-instalação

```bash
python scripts/audit-zips.py        # repo × skills instaladas
pwsh scripts/verify-cli.ps1         # inventário de CLIs (Windows)
python scripts/quality-gate.py      # o gate inteiro, offline
```

Compatibilidade por SO: [`COMPATIBILITY.md`](COMPATIBILITY.md). Uso offline:
[`OFFLINE-MODE.md`](OFFLINE-MODE.md).
