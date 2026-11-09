# Limitações conhecidas neste ambiente

Ferramentas instaladas que **parecem** funcionar pelo comando, mas não entregam a capacidade que o nome
promete. Registro aqui para não repetir a suposição.

## REA (Reverse Engineering Agent)

| Campo | Valor verificado (2026-11-08) |
|---|---|
| Versão | `rea-agents@6.8.0` |
| Tamanho | 281 MB (9.064 arquivos) |
| Comando | `rea --version` → 6.8.0 ✅ |
| Estado | **`INSTALLED_NO_ENGINE`** |
| `rea analyze` PE | ❌ `provider_unavailable`, exit 1 |
| `rea analyze` ELF | ❌ `provider_unavailable`, exit 1 |
| `rea doctor` | 21 checks, 19 falhas |

**Engines ausentes:** `ghidra` (`GHIDRA_INSTALL_DIR` não setado), `ida` (`REA_IDA_MCP_CONFIG`),
`jadx` (`REA_JADX_MCP_JAR`), `kuna` (`REA_KUNA_COMMAND`), `hopper` (não suportado em Windows).

**Providers presentes (não são engines de análise):** `rea-dotnet-static` (3/3), `sqlite` (1/1),
`rea-artifact-graph` (2/3, e não aceito como `--provider analyze`), `native-macos` (0/4, host errado).

**Para desbloquear:**

- **PE no Windows:** Ghidra 12.1.x + `GHIDRA_INSTALL_DIR`
- **ELF:** Ghidra no **WSL**, ou IDA, ou Kuna
- **Limitação:** Ghidra P0 no Windows aceita apenas PE e raw 6502

**Consequência para as skills:** `dz23-reverse-engineer-anything` declara desmontagem/emulação como
`BLOCKED_BY_EXTERNAL_DEPENDENCY` e usa `re_toolkit.py` (parse estrutural) como fallback.

## Ferramentas ausentes que bloqueiam fluxo

Registradas em detalhe em [`recommended.md`](recommended.md). As que mais bloqueiam:

| CLI | Skill afetada | Efeito |
|---|---|---|
| `openssl` | devops, RE | TLS/certificado/hash indisponível |
| `make` | devops, backend | build via Makefile não roda |
| `helm` / `terraform` | devops | IaC e K8s declarativo `BLOCKED` |
| `psql` | backend, performance | `EXPLAIN` em Postgres `BLOCKED` |
| `k6` / `ab` / `siege` | performance | load test `BLOCKED` |
| `semgrep` / `gitleaks` | backend, devops | análise estática `BLOCKED` |

## Armadilhas de presença × funcionamento

| CLI | Instalado | Funciona | Observação |
|---|---|---|---|
| `kubectl` | ✅ | ❌ | sem contexto (`kubectl config current-context` falha) |
| `docker` | ✅ | ✅ | daemon ativo, poucas imagens |
| `rea` | ✅ | ⚠️ parcial | sem engine de análise |
| `objdump`/`readelf` | ✅ | ⚠️ parcial | toolchain GNU do Windows; sobre ELF Linux o comportamento é limitado |

## Regra

**Instalado ≠ disponível ≠ funcional.** O padrão DZ23 exige verificar a capacidade, não a presença:

```bash
# presença
Get-Command <cli>

# funcionamento
<cli> --version
<cli> <operação real que a skill vai usar>
```
