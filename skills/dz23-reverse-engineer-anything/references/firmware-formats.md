# Formatos de firmware

Fatos de reconhecimento por formato. Tudo verificável com `xxd`/`binwalk` e coberto por `scripts/file_triage.py`.

## ESP32 / ESP-IDF — flash image e app image
**Flash image** reconhecida pela **tabela de partição**:
- entradas de **32 bytes**, magic `0x50AA` (`aa 50` em LE);
- tabela começa no setor `0x8000` (padrão) com offset alternativo configurável;
- pode haver **uma** entrada MD5 (`0xEBEB`) cobrindo as entradas anteriores;
- a tabela termina com entrada vazia (`aa 50` + tipo/subtipo `00 00`) dentro de `0xC00` bytes.

**App image** (`esp_image_header_t`): magic `0xE9` no primeiro byte, seguido de número de segmentos, `spi_mode`, `spi_speed`, e carga por segmento (`load_addr`, `data_len`). Bootloader e cada partição de app são app images — decodifique os headers de cada uma.

Layout típico: `0x0` bootloader → `0x8000` tabela → `0x10000` app (`factory`) → `0x100000+` (nvs, ota, spiffs/littlefs).

```bash
xxd -s 0x8000 -l 64 flash.bin        # deve começar com aa 50
binwalk flash.bin | head             # mostra offsets das assinaturas
```

## U-Boot legacy uImage
Header de **64 bytes**, magic **`0x27051956`** (BE, bytes `27 05 19 56` no arquivo).
Campos: `ih_hcrc`, `ih_time`, `ih_size`, `ih_load`, `ih_ep`, `ih_os`, `ih_arch`, `ih_type`, `ih_comp`, `ih_name` e o **CRC do payload** em `ih_dcrc`.

```bash
xxd -l 64 uImage.bin                 # magic + tamanho + load address
# verificação de CRC: uImage é header + payload comprimido
dd if=uImage.bin of=payload.bin bs=64 skip=1
# ih_comp: 0=none 1=gzip 2=bzip2 3=lzma 4=lzo 5=lz4 6=zstd
```
`ih_load`/`ih_ep` dizem onde o bootloader carrega e para onde salta — é o dado que permite emular.

## U-Boot FIT image
FIT é um **DTB** com nós `/images/<nome>` e `/configurations`. Magic DTB `0xD00DFEED`.
- `/images/…/data` (inline) ou referência externa;
- `hash@1` (sha256) e `signature@1` por imagem;
- verificar hash exige respeitar o `algo` declarado; **assinatura** exige a chave pública correta.
- `fdtget`/`dtc` decompilam o FIT para `.dts` legível — faça isso antes de tentar "extrair por offset".

```bash
dtc -I dtb -O dts -f image.its -o fit.dts && grep -A3 'images {' fit.dts
```
Payload assinado **não** fica em claro; se `data` estiver ausente, o conteúdo é referência externa.

## UF2 e DfuSe
**UF2**: blocos de **512 bytes** com magic no início `0x0A324655` (`55 46 32` = "UF2") e `0x9E5D5157` no offset 4, magic final `0x0AD0BC05` no offset 508. Campo `targetAddr` indica onde gravar. É o formato do drag-and-drop de placas (RP2040, STM32 via bootloader).

```bash
xxd -l 32 firmware.uf2               # 55 46 32 0a ...
# concatenar payloads por targetAddr respeitando ordem — não é "um binário"
```

**DfuSe**: container com magic `DfuSe` (ASCII) + versão + `bcdDevice`; cada imagem tem `bcdDevice`/`bcdDFU`/`wSectors`/endereço de destino. Usar `dfu-util` **somente leitura** (`-U` dump) se autorizado.

## Devicetree (DTB)
Magic `0xD00DFEED`; header com `totalsize`, `off_dt_struct`, `off_dt_strings`, `boot_cpuid`.
```bash
dtc -I dtb -O dts board.dtb -o board.dts
grep -E 'compatible|reg =|model' board.dts | head -20     # SoC, memória, periféricos
```
O `compatible` do nó raiz identifica a placa/SoC — melhor ponto de partida para achar o kernel certo.

## SquashFS / CramFS / JFFS2 / UBI
| Formato | Reconhece por | Extrai com |
|---|---|---|
| squashfs | `hsqs` (`sqsh` em BE) | `unsquashfs -d out img` |
| cramfs | magic `0x28CD3D45` | `cramfsck -x out img` |
| jffs2 | magic `0x1985` little endian nas nodes | `jefferson` / `jffs2extract` |
| UBI | `UBI#` no início | `ubireader_extract_images` |
| ext2/3/4 | `53 EF` em offset 0x438 | `debugfs`/`e2ls` (montar em loop é risco) |

SquashFS costuma estar **dentro** de outra imagem: ache o offset (binwalk) e extraia a partir dele, não do arquivo inteiro.

## Intel HEX e SREC (texto)
```
:10 0000 00 0C943000099401... 7B      ← Intel HEX: len, addr, type, data, checksum
S3 0D 0000 0C943000... 5A            ← SREC: type, count, address, data, checksum
```
Converta para binário respeitando os endereços (não concatene cegamente): gaps entre registros são reais.

```bash
objcopy -I ihex -O binary firmware.hex firmware.bin
objcopy -I srec -O binary firmware.srec firmware.bin
```

## Kernel modules e ELF notes
- `.ko` é ELF `ET_REL` com seção `.modinfo` (nome, vermagic, depends). `modinfo x.ko` lê sem carregar.
- `.notes` (ELF notes) traz build-id, ABI e às vezes proveniência — útil para casar binário com release.

## Saída
Formato confirmado por magic (com offset), campos de header relevantes, offset e tamanho de cada região, e a próxima ação (extrair/emular).
