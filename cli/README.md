# CLIs — visão geral

Guia das ferramentas de linha de comando que as skills usam. O inventário foi levantado **nesta máquina
(Windows 11 + PowerShell + WSL)**, não copiado de uma lista genérica.

## Números reais

Fonte de verdade: **`scripts/verify-cli.ps1`** — o inventário é **gerado por script**, não escrito à mão.
Rode e compare:

```powershell
pwsh scripts/verify-cli.ps1 -Json
```

| | Quantidade |
|---|---|
| CLIs procuradas pelo script | **117** |
| **Disponíveis** (no `PATH`) | **59** |
| **Ausentes** | **58** |

> Histórico: o plano original falava em "48+ instaladas, 23 faltando". Levantamentos manuais deram 58/56 e
> 45/39 em listas diferentes — cada lista produzia um número. A divergência era o sintoma: **contagem
> manual não é inventário**. Agora existe uma única fonte (`verify-cli.ps1`) e os documentos citam o que
> ela mediu.

## Índice

| Arquivo | Conteúdo |
|---|---|
| [`required.md`](required.md) | as 58 disponíveis, por categoria, e o que cada skill exige |
| [`recommended.md`](recommended.md) | as 56 ausentes, com prioridade ALTA/MÉDIA/BAIXA |
| [`install-windows.md`](install-windows.md) | `winget` / `choco` / `scoop`, comando por CLI |
| [`install-linux.md`](install-linux.md) | `apt` / `brew` / `curl \| sh` |
| [`verify.md`](verify.md) | como rodar a verificação automatizada |
| [`known-limitations.md`](known-limitations.md) | ferramentas instaladas que **não** entregam a capacidade (REA, kubectl sem contexto) |

## Como verificar sua própria máquina

```powershell
pwsh scripts/verify-cli.ps1
```

Saída: duas listas (disponíveis / faltando) e um resumo por categoria.

## Regra das skills sobre CLI

Nenhuma skill instala ferramenta por conta própria. Se falta uma dependência, o estado é
`BLOCKED_BY_EXTERNAL_DEPENDENCY` **com o nome da dependência e o comando de instalação** — e o agente
segue com o que for possível sem ela, declarando o que ficou de fora.

## Ferramentas base (todas as skills)

| CLI | Para quê | Obrigatória? |
|---|---|---|
| `git` | versionamento, diff, blame | sim |
| `python` (3.10+) | scripts das skills | sim |
| `node` (20+) | MCP, Playwright, tooling JS | sim |
| `rg` (ripgrep) | busca de código | sim |
| `jq` | parse de JSON | sim |
| `curl` | HTTP, health check | sim |

## Ferramentas por domínio

| Domínio | CLIs |
|---|---|
| Containers/Deploy | `docker`, `docker-compose`, `kubectl`, `trivy` |
| Frontend | `node`, `npx`, `playwright` |
| Dados | `sqlite3` (presente); `psql`/`redis-cli`/`mongosh` (ausentes) |
| RE/Binário | `objdump`, `readelf`, `strings`, `nm`, `strip`, `objdump` |
| Sistema | `pwsh`, `winget`, `7z`, `ffmpeg`, `certutil` |

## O que este guia **não** faz

- Não instala nada. Instalação é decisão sua.
- Não garante que a CLI funciona: presença no `PATH` ≠ funciona. `docker` pode estar instalado com o
  daemon parado, `kubectl` pode estar sem contexto.
- Não cobre CLIs privadas/de assinatura paga.
