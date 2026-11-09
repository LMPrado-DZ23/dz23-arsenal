# Instalação de CLIs — Windows

Três gerenciadores. `winget` vem com o Windows 11 e é o caminho mais curto.

## ALTA prioridade

```powershell
# openssl (não vem com o Windows por padrão)
winget install ShiningLight.OpenSSL.Light
# alternativa: choco install openssl

# make
winget install ezwinports.make
# alternativa: choco install make

# helm
winget install Helm.Helm

# terraform
winget install Hashicorp.Terraform
# alternativa OpenTofu: winget install OpenTofu.OpenTofu

# go
winget install GoLang.Go

# semgrep
pip install semgrep

# gitleaks
winget install Gitleaks.Gitleaks

# hadolint
winget install hadolint.hadolint

# act
winget install nektos.act

# k9s
winget install Derailed.k9s

# produtividade
winget install junegunn.fzf
winget install sharkdp.bat
winget install sharkdp.fd
winget install JesseDuffield.lazygit
winget install dandavison.delta
```

## MÉDIA prioridade

```powershell
# bancos
winget install PostgreSQL.PostgreSQL   # traz psql
winget install Redis.Redis             # traz redis-cli
winget install MongoDB.Shell           # mongosh
winget install Oracle.MySQL            # mysql

# http
winget install httpie.httpie
# grpcurl: sem winget oficial — choco install grpcurl  OU  go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

# python tooling
pip install poetry
winget install jdx.mise

# arquivamento
winget install 7zip.7zip   # já presente nesta máquina; se faltar, é este

# segurança
pip install bandit
winget install snyk.snyk

# rede
winget install Insecure.Nmap
winget install WiresharkFoundation.Wireshark   # traz tcpdump via Npcap (parcial)

# download
winget install GNU.Wget2
```

## BAIXA prioridade

```powershell
winget install eza-community.eza
winget install Neovim.Neovim
winget install k6.k6
winget install jqlang.jq        # já presente
winget install LLVM.LLVM        # traz clang
```

## Alternativas por gerenciador

| Gerenciador | Instalar | Quando usar |
|---|---|---|
| `winget` | nativo no Windows 11 | primeiro caminho |
| `choco` | `Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))` | quando não há pacote no winget |
| `scoop` | `irm get.scoop.sh \| iex` | CLIs de usuário, sem admin |

## Depois de instalar

```powershell
# recarregue o PATH nesta sessão, ou abra um terminal novo
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# verifique
pwsh scripts/verify-cli.ps1
```

## Avisos

- **`winget install` pode pedir aceite de termos.** Use `--accept-package-agreements --accept-source-agreements` em automação.
- **Instalar não é ter.** `openssl version` e `make --version` são a prova; presença no menu Iniciar não é.
- **Nada neste repo instala automaticamente.** Os comandos acima são para você rodar, com decisão sua.
