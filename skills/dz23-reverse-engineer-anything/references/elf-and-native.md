# ELF, PE e Mach-O

## ELF — o que ler primeiro
```bash
readelf -h alvo                  # classe, endianness, machine, entry, tipo (EXEC/DYN)
readelf -S alvo                  # seções (.text .data .rodata .bss .init_array)
readelf -l alvo                  # segmentos (LOAD/RWX) — mapa de memória
readelf -s alvo | head -40       # símbolos (se não stripped)
readelf -d alvo                  # dependências dinâmicas e flags
readelf -n alvo                  # notas (build-id, ABI, GNU property)
```

### Sinais que valem achado
| Achado | Significa |
|---|---|
| Entry **fora** de `.text` | packer/stub ou binário ofuscado |
| Segmento `RWX` | gravável e executável — JIT, packer ou risco |
| `.text` com entropia > 7.5 | comprimido/cifrado |
| Sem `.comment`/`.note.gnu.build-id` | build sem toolchain normal |
| `NEEDED` vazio mas importa `dlopen` | carrega biblioteca em runtime |
| `.init_array` com vários ponteiros | construtores/anti-debug antes de `main` |

## Hardening (o que o atacante explora)
```bash
readelf -l alvo | grep -E 'GNU_STACK|GNU_RELRO'   # NX e RELRO
readelf -d alvo | grep -E 'BIND_NOW|FLAGS'
# PIE: Type DYN no -h; canary: símbolo __stack_chk_fail; FORTIFY: __*_chk
```
| Proteção | Presente se | Ausente = risco |
|---|---|---|
| NX | `GNU_STACK` sem `E` | stack executável |
| RELRO full | `BIND_NOW` + `GNU_RELRO` | GOT sobrescrevível |
| PIE | `Type: DYN` + `Entry` relativo | sem ASLR efetivo |
| Canary | `__stack_chk_fail` | overflow de stack direto |
| FORTIFY | `__memcpy_chk`, `__printf_chk` | sem checagem de tamanho |

Isso é **observação do binário**, não auditoria de vulnerabilidade — quem faz essa análise é `security-review`.

## PE (Windows)
```bash
objdump -x alvo | head -60         # headers, seções, imports
strings -n 6 alvo | grep -iE '\.pdb|Visual C\+\+|mingw|Go build'
```
- Seções com `RawSize` 0 e `VirtualSize` alto → unpacking em memória.
- Import de `VirtualAlloc`/`VirtualProtect`/`CreateRemoteThread` + `LoadLibrary` em combinação = indício de injeção (indício, não prova).
- Assinatura Authenticode: presença **não** prova legitimidade — valide a cadeia e o `subject`.
- `.NET` (`mscoree` import) → camada gerenciada; o nativo é só o host.

## Mach-O
```bash
otool -h alvo        # header, cpu, filetype
otool -l alvo        # load commands (LC_SEGMENT, LC_LOAD_DYLIB)
nm -m alvo 2>/dev/null | head
```
Fat binary: `lipo -info`. Se `__TEXT` alto entropia e `LC_ENCRYPTION_INFO` presente → criptografado (App Store).

## Símbolos: nome real vs rótulo
- Não stripped → use o nome do símbolo, com evidência (`readelf -s`).
- Stripped → **`sub_<endereço>`** até prova. Nunca invente nome (ex.: `decrypt_password`) sem cadeia de evidência até a string/syscall.
- Nome inferido entra como `sub_4012A0 (provável parser de config)` — o parêntese é hipótese, o nome não.
- `dlopen`/`dlsym` por string: procure a string literal; o símbolo aparece só em runtime.

## Chamadas e fluxo (estático)
```bash
objdump -d alvo | less                      # disassembly linear
objdump -d --start-address=0x401000 --stop-address=0x401200 alvo
# xrefs: use Rizin/Rz-bin ou Ghidra headless (ver static-analysis.md)
```
Regra: leia a função de **entrada para fora** — `main`, depois `main`→callees. Disassembly linear em binário com dados no meio de `.text` gera lixo: confie no fluxo de controle, não no `objdump` puro.

## Saída
Mapa de seções/segmentos, hardening (com evidência), lista de símbolos reais, candidatos a função por offset, e o que está empacotado/cifrado.
