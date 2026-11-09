# Verificação de CLIs

## Comando único

```powershell
pwsh scripts/verify-cli.ps1
```

```bash
# Linux/macOS
bash scripts/verify-cli.sh 2>/dev/null || echo "use o one-liner abaixo"
```

## O que o script faz

1. Percorre uma lista fixa de ~114 CLIs.
2. Usa `Get-Command` (PowerShell) ou `command -v` (shell) para cada uma.
3. Separa em **disponíveis** e **faltando**.
4. Agrupa por categoria (VCS, runtimes, containers, dados, sistema).
5. Exit `0` se todas as obrigatórias existem; exit `1` se falta alguma obrigatória.

## O que ele **não** faz

- **Não valida funcionamento.** `docker` instalado com daemon parado aparece como disponível.
- **Não checa versão mínima.** `node` 14 passa no teste de presença, mas o MCP exige 20+.
- **Não instala nada.**

## One-liner manual (para colar em qualquer shell)

```bash
for c in git python3 node npm rg jq curl docker kubectl trivy openssl make; do
  command -v "$c" >/dev/null 2>&1 && echo "OK    $c" || echo "FALTA $c"
done
```

## Verificação de versão (quando a presença não basta)

| CLI | Versão mínima | Comando de prova |
|---|---|---|
| `node` | 20 | `node --version` |
| `python` | 3.10 | `python --version` |
| `docker` | 24 | `docker version --format '{{.Server.Version}}'` |
| `kubectl` | 1.28 | `kubectl version --client` |
| `trivy` | 0.50 | `trivy --version` |

## Verificar que o daemon/contexto funciona

Presença no `PATH` não prova que o serviço responde:

```bash
docker info >/dev/null 2>&1 && echo "docker OK" || echo "docker instalado, daemon parado"
kubectl config current-context 2>/dev/null || echo "kubectl instalado, sem contexto"
trivy --version 2>/dev/null | head -1
```

## Interpretando o resultado

| Saída | Significado | Ação |
|---|---|---|
| tudo `OK` | CLIs base presentes | siga |
| falta só BAIXA prioridade | dá para trabalhar | instale sob demanda |
| falta ALTA | parte das skills vai declarar `BLOCKED` | ver `install-windows.md` |
| `docker` OK mas daemon parado | CLI presente, serviço não | iniciar Docker Desktop |
| `kubectl` OK mas sem contexto | CLI presente, cluster não | `kubectl config use-context` |

## Registrar o resultado

O script aceita `-Json` para gerar saída estruturada, útil para anexar ao relatório de um deploy:

```powershell
pwsh scripts/verify-cli.ps1 -Json > cli-state.json
```
