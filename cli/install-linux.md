# Instalação de CLIs — Linux e macOS

## Debian / Ubuntu (apt)

```bash
sudo apt update

# ALTA
sudo apt install -y openssl make golang-go
sudo apt install -y fzf bat fd-find ripgrep jq
sudo apt install -y git curl wget unzip zip
sudo apt install -y nmap tcpdump
pip install --user semgrep bandit
# helm / terraform / act / k9s / hadolint / gitleaks: ver bloco "binários oficiais"

# MÉDIA
sudo apt install -y postgresql-client redis-tools mongodb-clients default-mysql-client
sudo apt install -y python3-poetry httpie
sudo apt install -y clang

# BAIXA
sudo apt install -y neovim eza k6
```

> No Debian/Ubuntu, `bat` instala como `batcat` e `fd` como `fdfind` por conflito de nome. Crie alias:
> `alias bat=batcat; alias fd=fdfind`.

## macOS (brew)

```bash
brew update

# ALTA
brew install openssl make go helm terraform act k9s hadolint gitleaks
brew install fzf bat fd lazygit git-delta
pip3 install --user semgrep

# MÉDIA
brew install postgresql redis mongosh mysql-client
brew install poetry mise httpie grpcurl
brew install bandit snyk

# BAIXA
brew install eza neovim k6 nmap
```

No macOS, use `gmake` se precisar de GNU make (`brew install make` instala como `gmake`).

## Binários oficiais (qualquer Linux/macOS)

Ferramentas que distribuem binário estático — mais confiável que repo de distro:

```bash
# terraform
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp.gpg
sudo apt install terraform

# helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# act
curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# k9s
curl -sS https://webinstall.dev/k9s | bash

# hadolint
wget -O /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64
chmod +x /usr/local/bin/hadolint

# gitleaks
curl -sSfL https://raw.githubusercontent.com/gitleaks/gitleaks/master/scripts/install.sh | sh -s -- -b /usr/local/bin

# k6
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
  --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" \
  | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt update && sudo apt install k6
```

## Verificação

```bash
for c in git python3 node rg jq curl openssl make docker trivy helm terraform; do
  if command -v "$c" >/dev/null 2>&1; then
    printf 'OK   %-12s %s\n' "$c" "$("$c" --version 2>&1 | head -1)"
  else
    printf 'FALTA %s\n' "$c"
  fi
done
```

## Avisos

- **`curl | bash` executa código de terceiros como root.** Prefira baixar, inspecionar e então executar.
- **`apt install terraform` pode falhar** — prefira o repositório oficial da HashiCorp (bloco acima).
- **Instalar não é funcionar.** Verifique com `--version`, não com `which`.
- Nada neste repo executa instalação por você.
