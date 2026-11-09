# Triagem do alvo

## Regra
Formato é o que os **bytes** dizem, não a extensão. `.bin` pode ser squashfs; `.img` pode ser tabela de partição; `.fw` pode ser ELF comprimido.

## Identificação em 60 segundos
```bash
sha256sum alvo                        # identidade da evidência (obrigatório no relatório)
ls -l alvo                            # tamanho real
file alvo                             # palpite do libmagic (não é prova)
xxd -l 64 alvo                        # magic bytes literais
xxd -s 0x100 -l 64 alvo               # sonda em offset alternativo
strings -n 8 alvo | head -40          # indício de plataforma/versão
```
No Windows: `certutil -hashfile alvo SHA256`, `Format-Hex -Path alvo -Count 64`.

## Magic bytes que importam
| Assinatura | Offset | Formato |
|---|---|---|
| `7F 45 4C 46` (`\x7fELF`) | 0 | ELF |
| `4D 5A` (`MZ`) | 0 | PE (Windows) |
| `CF FA ED FE` / `CA FE BA BE` | 0 | Mach-O (thin / fat) |
| `27 05 19 56` | 0 | U-Boot legacy uImage |
| `D0 0D FE ED` | 0 | FIT / devicetree (DTB) |
| `hsqs` / `sqsh` | variável | squashfs (little/big endian) |
| `1F 8B` | variável | gzip |
| `FD 37 7A 58 5A` | variável | xz |
| `55 AA` (32 B por entrada, tipo) | setor 0x800 | tabela de partição ESP |
| `E9` + `LDA` | 0 | ESP app image |
| `55 46 32` (`UF2` → `0x0A324655`) | 0 | UF2 |
| `:10` / `:02000004` | 0 | Intel HEX (texto) |
| `S0` / `S3` | 0 | SREC (texto) |
| `UBI#` | 0 | UBI (NAND) |
| `0x27051956` em BE | 0 | uImage (redundante com acima) |

Se nenhuma casar: pode ser **cifrado**, **comprimido sem header** ou **região de flash crua**. Aí entra a entropia.

## Entropia (Shannon por bloco)
```bash
# blocos de 4 KiB; > 7.5 bits/byte sustentado = compressão ou cifra
python - <<'PY'
import math, sys
from collections import Counter
data = open(sys.argv[1] if len(sys.argv) > 1 else "alvo", "rb").read()
blk = 4096
for off in range(0, min(len(data), 64 * 1024), blk):
    chunk = data[off:off + blk]
    if not chunk: break
    c = Counter(chunk); n = len(chunk)
    h = -sum((v / n) * math.log2(v / n) for v in c.values())
    print(f"0x{off:08x}  {h:.3f}")
PY
```
Interpretação honesta:
- **~8,0** em bloco inteiro → cifrado ou comprimido de alta entropia.
- **~7,9–8,0 com estrutura fraca** → comprimido (tente zlib/xz/lzma).
- **< 6,0** → texto/código/estrutura legível.
- **Transição brusca de entropia** → fronteira entre header e payload (ótimo marcador de offset).

Nunca conclua "cifrado" sem tentar `binwalk -e`, `xz -t`, `gzip -t` e sem citar a entropia medida.

## Arquitetura (quando já é ELF/PE)
```bash
readelf -h alvo | grep -E 'Class|Data|Machine|Type|Entry'
# Class: ELF32/64 · Data: 2's complement little/big endian · Machine: ARM/MIPS/x86-64/RISCV
objdump -f alvo        # arquitetura e formato
```
Para firmware sem container, a arquitetura só se confirma após extração (ou por strings de toolchain: `gcc (Buildroot`, `musl`, `uClibc`, `esp-idf`, `FreeRTOS`).

## Empacotamento
```bash
upx -l alvo            # UPX? (magic UPX! no fim do arquivo)
strings -n 6 alvo | grep -iE 'upx|mprotect|ptrace|/proc/self' | head
```
Packer genérico: seção `.text` com alta entropia **e** imports mínimos (`ptrace`, `mprotect`, `mmap`) — indício, não prova.

## Plataforma pelo vocabulário
| String | Indício |
|---|---|
| `Buildroot`, `OpenWrt`, `BusyBox` | roteador/embedded Linux |
| `esp-idf`, `FreeRTOS`, `ESP32` | ESP32 |
| `U-Boot`, `bootcmd`, `fdt_` | bootloader ARM |
| `squashfs`, `jffs2`, `ubi` | rootfs de firmware |
| `libc.so.6`, `ld-musl-` | glibc vs musl |
| `Microsoft Visual C++`, `.pdb` | binário Windows |
| `Go build ID`, `runtime.main` | binário Go |
| `Rust`, `cargo`, `panic!` | binário Rust |

## Saída da triagem
```
ALVO: <path> | sha256: <hash> | tamanho: <bytes>
FORMATO: <do magic> | ARQUITETURA: <arch> | ENDIANNESS: <le/be>
ENTROPIA: <média por bloco> | FRONTEIRAS: <offsets de transição>
EMPACOTAMENTO: <upx/genérico/nenhum observado>
PLATAFORMA (indício): <strings>
PRÓXIMO PASSO: <estática | extração | emulação>
```
