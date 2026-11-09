# CLIs — visão geral

Guia das ferramentas de linha de comando que as skills usam. O inventário foi levantado **nesta máquina
(Windows 11 + PowerShell + WSL)**, não copiado de uma lista genérica.

## Números reais

| | Quantidade |
|---|---|
| CLIs procuradas nesta auditoria | **114** |
| **Disponíveis** (no `PATH`) | **58** |
| **Ausentes** | **56** |

> A promessa original era "48+ instaladas, 23 faltando". O levantamento real deu 58 e 56. Os números
> acima são os verificados com `Get-Command`, um por um — a diferença não é detalhe: metade das
> ferramentas que o guia supunha instaladas não está no `PATH` desta máquina.

## Índice

| Arquivo | Conteúdo |
|---|---|
| [`required.md`](required.md) | as 58 disponíveis, por categoria, e o que cada skill exige |
| [`recommended.md`](recommended.md) | as 56 ausentes, com prioridade ALTA/MÉDIA/BAIXA |
| [`install-windows.md`](install-windows.md) | `winget` / `choco` / `scoop`, comando por CLI |
| [`install-linux.md`](install-linux.md) | `apt` / `brew` / `curl \| sh` |
| [`verify.md`](verify.md) | como rodar a verificação automatizada |

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
