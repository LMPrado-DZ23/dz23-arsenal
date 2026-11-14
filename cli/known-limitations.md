# Limitações conhecidas neste ambiente

Ferramentas instaladas que **parecem** funcionar pelo comando, mas não entregam a capacidade que o nome
promete. Registro aqui para não repetir a suposição.

## REA (Reverse Engineering Agent)

| Campo | Valor verificado (2026-11-14 — substitui o registro de 2026-11-08) |
|---|---|
| Versões | `rea-agents@6.8.0` (Windows) · **6.9.0** (WSL) |
| Estado | **`AVAILABLE`** — engines instalados **e** configurados |
| Ghidra | 12.1.4 PUBLIC, `GHIDRA_INSTALL_DIR` setado nos dois hosts |
| jadx | 0.7.1, `REA_JADX_MCP_JAR` setado |
| Desmontagem | ✅ provada — `procedure_pseudo_code` devolveu `entry` de PE x86-64 |
| APK | ✅ provado — 20.990 classes, 1.842 recursos |
| Apoio | apktool 3.0.3 · adb 37.0.1 · WABT 1.0.42 · unblob 26.6.4 · tshark |
| `rea doctor` | `ghidra` ok (+8 subchecagens) e `jadx` ok; restam `ida`/`kuna` ausentes |

**Engines ainda ausentes:** `ida` (`REA_IDA_MCP_CONFIG`), `kuna` (`REA_KUNA_COMMAND`), `jeb`
(cliente em `127.0.0.1:8425`), `hopper` (só macOS).

**Armadilha que gerou dois diagnósticos errados seguidos (2026-11-08):** o REA estava instalado mas os
servers MCP subiam **sem** a env de provider, então a CLI respondia `provider_unavailable` em PE e ELF
mesmo com tudo no disco. **Instalado ≠ configurado no processo.** O estado só vale se medido com a env
do processo que vai executar.

**Como iniciar:**

- Windows/WSL: `. D:\IA-Workspace\Deepseek\tools\rea-env.ps1` · `source /mnt/d/.../tools/rea-env.sh`
- Confira: `rea doctor` (Ghidra e jadx `ok: true`) antes de declarar `AVAILABLE`
- No DSH, os servers MCP `rea` e `rea-linux` já recebem a env pela config
  (`.dsh\cordis.patch.yml` e `.dsh\profiles\desktop\cordis.patch.yml`)

**Limitação:** Ghidra P0 no Windows aceita apenas PE e raw 6502; para ELF use o WSL. Ghidra no Windows
também não renomeia nem comenta (limite do P0).

**Consequência para as skills:** `dz23-reverse-engineer-anything` passa a usar o REA para desmontagem,
pseudocódigo, APK e wasm, mantendo `re_toolkit.py` como fallback offline para firmware e parse
estrutural.

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
| `rea` | ✅ | ✅ | engines configurados; a env é lida no startup do processo |
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
