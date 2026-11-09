# Instalação e ferramental

## DeepSeek Harness (DSH)
1. Copie `dz23-reverse-engineer-anything/` para `C:\Users\<usuário>\.agents\skills\`.
2. Descoberta lê `SKILL.md` na raiz — sem reinício.
3. Invoque por `/dz23-reverse-engineer-anything` ou por descrição ("analise este dump de flash").
4. `~/.claude/skills` e `~/.codex/skills` são junction para `~/.agents/skills`.

## Estrutura
```
dz23-reverse-engineer-anything/
  SKILL.md
  README.md
  CHANGELOG.md
  VERSION
  PROMPT-ATIVACAO.txt
  references/ (11)
  templates/ (4)
  scripts/file_triage.py
  scripts/validate_skill.py
  evals/evals.json (15)
```

## Ferramental por área
| Área | Ferramenta | Nota |
|---|---|---|
| Triagem | `file`, `xxd`, `binwalk`, `strings`, `sha256sum` | base, quase sempre presente |
| ELF/PE | `readelf`, `objdump`, `nm`, `patchelf` | binutils |
| Desmontagem | Ghidra (headless), Rizin/Cutter, Hopper | Ghidra é gratuito e scriptável |
| Depuração | GDB (+ pwndbg/gef), Rizin `-d` | GDB suficiente na maioria |
| Dinâmica | `strace`, `ltrace`, `frida`, `bpftrace` | frida para app empacotado |
| Firmware | `binwalk`, `unsquashfs`, `ubireader`, `jefferson`, `dtc`, `objcopy` | extratores por formato |
| Emulação | `qemu-user`, `qemu-system-*`, Unicorn | qemu-user resolve 70% dos casos |
| Fuzzing | AFL++, libFuzzer, honggfuzz | com instrumentação |

**Esta skill não instala nada.** Ferramenta ausente → `BLOCKED_BY_EXTERNAL_DEPENDENCY` com o nome exato do que falta (e o comando de instalação fica a critério do dono).

## Verificar o que existe na máquina
```bash
for t in file xxd binwalk strings objdump readelf nm gdb rizin ghidra dtc unsquashfs qemu-arm qemu-mipsel strace upx; do
  printf '%-14s %s\n' "$t" "$(command -v $t >/dev/null 2>&1 && echo AVAILABLE || echo UNAVAILABLE)"
done
```
No Windows, `Get-Command <nome>` em vez de `command -v`. Rode isso **antes** de prometer análise que depende da ferramenta.

## Onde os artefatos vão
No projeto do alvo, não na pasta da skill:
```
projects/<alvo>/
  re/
    RE-REPORT.md        (templates/re-report.md)
    TRIAGE.md           (templates/target-triage.md)
    FIRMWARE-MAP.md     (templates/firmware-map.md)
    LEDGER.md           (templates/findings-ledger.md)
    work/extract/       (extração; fora de versionamento)
```
`work/` e binários **nunca** vão para o git — o repositório guarda relatório, hash e achado.

## Verificação da skill
```bash
python scripts/validate_skill.py
python scripts/file_triage.py <arquivo>
```

## Uso combinado
- `rea` / `reverse-engineer-anything` — REA completo para app, APK, Electron, bundle web.
- `security-review` — quando o alvo é avaliação de vulnerabilidade.
- `api-and-contracts` — quando o protocolo descoberto vira contrato.
- `dz23-codebase-cartographer` — se o alvo vier acompanhado de código-fonte.
- `craft-anything` — investigação de software empacotado com memória de projeto.

## Quando **não** usar
Bug funcional em código que você possui (`diagnosing-bugs`), análise de repositório-fonte (cartographer) ou pergunta sobre comportamento de API pública (documentação). Engenharia reversa é para quando a **fonte não existe ou não é confiável**.
