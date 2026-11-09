# CLIs ausentes — com prioridade

**58 ferramentas** que **não estão** no `PATH` desta máquina (fonte: `scripts/verify-cli.ps1` — 117
procuradas · 59 disponíveis · 58 ausentes). A lista abaixo prioriza as de maior impacto; o total completo
sai do script.

> Nada aqui foi instalado. A lista existe para decidir com informação, não para empurrar instalação.

## ALTA — bloqueiam trabalho comum

| CLI | Para quê | Skill que sofre |
|---|---|---|
| `openssl` | TLS, certificados, hashes | devops, RE |
| `make` | build via Makefile | devops, backend |
| `helm` | charts Kubernetes | devops |
| `terraform` | IaC | devops |
| `go` | toolchain Go | backend, RE (binários Go) |
| `semgrep` | análise estática de segurança | backend, security |
| `gitleaks` | detecção de segredo no repo | devops, backend |
| `fzf` / `bat` / `fd` | produtividade de terminal | todas (informal) |
| `lazygit` / `delta` | git visual / diff legível | todas (informal) |
| `hadolint` | lint de Dockerfile | devops |
| `act` | rodar GitHub Actions local | devops |
| `k9s` | TUI de Kubernetes | devops |

## MÉDIA — destravam casos específicos

| CLI | Para quê | Skill |
|---|---|---|
| `psql` | cliente Postgres | backend, performance |
| `redis-cli` | cliente Redis | backend, performance |
| `mongosh` | cliente MongoDB | backend |
| `mysql` | cliente MySQL | backend |
| `poetry` / `mise` | ambiente Python | backend, performance |
| `httpie` | HTTP legível | todas |
| `grpcurl` | gRPC | backend |
| `zip` / `unzip` | arquivamento (nativo do PowerShell não basta) | todas |
| `nmap` / `tcpdump` | diagnóstico de rede | devops |
| `bandit` / `snyk` | segurança | backend |
| `tofu` (OpenTofu) | IaC alternativo | devops |
| `wget` | download | devops |

## BAIXA — conforto, não bloqueio

| CLI | Motivo |
|---|---|
| `eza` | `ls` melhorado (já tem `ls`) |
| `nvim` | editor (já tem `code`) |
| `k6` / `ab` / `siege` | load test (a skill declara `BLOCKED` sem eles) |
| `clang` | alternativa ao `gcc` presente |
| `mvn` / `gradle` | JVM build (só se projeto Java) |
| `cl` | MSVC (só se necessário) |
| `dotnet-ef` | EF Core CLI |
| `claude` / `codex` / `gemini` | CLIs de outros agentes |
| `tor` | anonimato (não é uso das skills) |
| `sh` / `which` / `envsubst` / `base64` / `md5sum` / `sha256sum` | existem dentro do Git Bash/WSL |
| `sed` / `awk` / `grep` | idem — presentes em `/usr/bin/` do Git Bash |

## Casos que **parecem** faltar mas existem

Antes de instalar, verifique se a ferramenta está em outro shell:

```powershell
# sed/awk/grep/sh/which estão no Git Bash
bash -c "sed --version; awk --version; grep --version"

# e no WSL
wsl -e sh -c "which sed awk grep"
```

`sha256sum`/`md5sum` têm equivalente nativo:
```powershell
Get-FileHash -Algorithm SHA256 arquivo
Get-FileHash -Algorithm MD5 arquivo
```

## Ordem sugerida (se for instalar)

1. `openssl`, `make` — custo baixo, bloqueiam muita coisa.
2. `semgrep`, `gitleaks` — segurança não é opcional em deploy.
3. `helm` + `terraform` — só se você realmente provisiona.
4. `fzf`, `bat`, `fd`, `delta` — ganho de produtividade imediato, sem risco.
5. O resto, sob demanda.

## Como instalar

- Windows: [`install-windows.md`](install-windows.md)
- Linux/macOS: [`install-linux.md`](install-linux.md)
- Verificar depois: [`verify.md`](verify.md)
