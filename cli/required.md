# CLIs disponíveis — inventário verificado

**59 ferramentas** presentes no `PATH` desta máquina. Fonte de verdade: `scripts/verify-cli.ps1`
(117 procuradas · 59 disponíveis · 58 ausentes). Data: 2026-11-08.

> Este arquivo documenta **por categoria** o que o script encontrou. Se a sua máquina divergir, rode o
> script — o número dele é o que vale.

## Controle de versão e GitHub

| CLI | Versão | Uso nas skills |
|---|---|---|
| `git` | 2.56.0 | todas |
| `gh` | 2.x | devops (repo, release, secret) |
| `scp` | — | devops (transferência) |
| `ssh` | — | devops (acesso remoto) |

## Runtimes e linguagens

| CLI | Versão | Uso |
|---|---|---|
| `node` | 26.13.0 | MCP, Playwright, tooling |
| `npm` | 11.20.0 | instalação de MCP |
| `npx` | — | executar pacotes sem instalar |
| `pnpm` | — | alternativa ao npm |
| `python` | 3.12.10 | **todas as skills** (scripts) |
| `python3` / `py` | — | aliases |
| `pip` | — | dependências Python |
| `uv` | — | ambiente Python rápido |
| `java` | — | JVM (alguns binários) |
| `dotnet` | — | .NET |
| `rustc` | — | compilação Rust |
| `cargo` | — | pacotes Rust |

## Containers, deploy e segurança

| CLI | Versão | Uso |
|---|---|---|
| `docker` | 29.9.2 | devops, e2e |
| `docker-compose` | — | devops |
| `kubectl` | 1.36.1 | devops (**sem contexto configurado**) |
| `trivy` | 0.76.1 | devops (scan de imagem/FS) |

## Ferramentas de build

| CLI | Uso |
|---|---|
| `gcc`, `g++`, `ld` | compilação nativa, análise de binário |
| `cmake` | build C/C++ |

## Inspeção de binário

| CLI | Uso nas skills |
|---|---|
| `objdump` | `reverse-engineer-anything` (desmontagem) |
| `readelf` | ELF header/seções |
| `strings` | cadeias de texto |
| `nm`, `strip` | símbolos |

> `readelf`/`objdump` aqui vêm do toolchain GNU do Windows. Para ELF Linux real, prefira rodar dentro de
> WSL ou container — o comportamento de `readelf` do Windows sobre binário Linux é limitado.

## Dados e utilitários

| CLI | Versão | Uso |
|---|---|---|
| `sqlite3` | — | banco local, provas |
| `jq` | 1.8.2 | parse JSON |
| `rg` | 15.2.0 | busca de código |
| `curl` | 8.21.0 | HTTP (Brotli confirmado) |
| `7z` | — | arquivos compactados |
| `ffmpeg` | — | mídia |

## Browser e mobile

| CLI | Uso |
|---|---|
| `playwright` | `e2e-browser-verifier` (cross-browser) |
| `adb` | mobile (Android) |
| `scrapling` | scraping com browser |

## Shell e sistema (Windows)

| CLI | Uso |
|---|---|
| `pwsh` / `powershell` | scripts `.ps1` |
| `winget` | instalação de pacotes |
| `code` | VS Code (CLI) |
| `wsl` | subsistema Linux |
| `cat`, `ls`, `bash` | utilitários via Git Bash |
| `tar` | arquivamento |
| `netstat`, `tasklist`, `reg`, `schtasks`, `certutil`, `bitsadmin` | diagnóstico Windows |
| `findstr`, `where` | busca e localização |
| `robocopy`, `xcopy` | cópia robusta |

## O que cada skill exige

| Skill | Obrigatório | Opcional |
|---|---|---|
| `spec-to-system-engine` | `git` | — |
| `codebase-cartographer` | `git`, `rg`, `python` | `jq` |
| `backend-data-architect` | `git`, `python` | `docker`, `sqlite3`, `psql` |
| `ultimate-pro-max` | `node`, `npx` | `playwright`, `lighthouse` |
| `devops-cloud-deployer` | `docker`, `git`, `trivy` | `kubectl`, `helm`, `terraform` |
| `e2e-browser-verifier` | `node`, `npx`, `playwright` | `rg` |
| `performance-scalability-engine` | `python`, `curl` | `lighthouse`, `k6`, `psql` |
| `reverse-engineer-anything` | `python` | `objdump`, `readelf`, `ghidra`, `qemu` |
| `autonomous-improvement-ultimate` | `git`, `python` | o que a skill chamada exigir |

## Armadilhas verificadas nesta máquina

1. **`kubectl` sem contexto** — instalado, mas `kubectl config current-context` falha. Ter a CLI não é
   ter cluster.
2. **`docker` com daemon ativo, mas sem imagens** — primeiro build puxa tudo.
3. **`openssl` ausente do PATH** — surpreendente em Windows, mas confirmado. Muitos scripts de TLS vão
   falhar com "openssl: not found".
4. **`make` ausente** — projetos com `Makefile` não compilam sem instalar.
5. **`sed`/`awk`/`grep` ausentes do PATH do PowerShell** — existem dentro do Git Bash
   (`/usr/bin/`), mas não são encontrados pelo shell padrão. Use `bash -c` ou `wsl`.
