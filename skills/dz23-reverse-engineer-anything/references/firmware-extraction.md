# Extração de firmware

## Regra
Extração é **read-only na origem**: você escreve em diretório de trabalho, nunca na imagem/dispositivo. Preserve o hash do original e registre o offset de cada artefato extraído.

## Fluxo
```bash
mkdir -p work/extract && cd work
sha256sum ../flash.bin > origem.sha256        # identidade da evidência
binwalk ../flash.bin                          # varredura de assinatura, sem extrair
binwalk -e --run-as=root ../flash.bin         # extrai (binwalk moderno usa extratores externos)
```
`binwalk -e` **não** extrai tudo: usa `unsquashfs`, `ubireader`, `jefferson`, `sasquatch`. Se o extrator não estiver instalado, o binwalk avisa — registre como `BLOCKED`, não como "extraiu vazio".

## Manual (quando a ferramenta falha)
Setores de flash não são contíguos. Extraia por **offset conhecido**, não por `dd` do arquivo inteiro:
```bash
# ESP32: tabela em 0x8000, app em 0x10000, tamanho vindo do header
xxd -s 0x8000 -l 0xC00 flash.bin | head -40
dd if=flash.bin of=app.bin bs=1 skip=$((0x10000)) count=$((app_size))
```
O tamanho do app está no header da app image (campo de tamanho do segmento) ou no fim do segmento — leia antes de cortar.

## SquashFS embutido
```bash
off=$(binwalk ../flash.bin | awk '/Squashfs/{print $1; exit}')
dd if=../flash.bin of=root.sqsh bs=1 skip=$((off))
unsquashfs -d rootfs root.sqsh
ls rootfs/etc/init.d 2>/dev/null; cat rootfs/etc/passwd 2>/dev/null | head
```
Se `unsquashfs` falhar com "not a squashfs": o offset está 1–4 bytes errado (procure `hsqs` com `grep -abo`).

## Assinatura e integridade
- Se o container tem hash/CRC declarado (uImage `ih_dcrc`, FIT `hash@1`, ESP imagem MD5), **verifique** e registre o resultado: extração que falha o CRC é achado, não erro seu.
- Imagem **assinada** não é imagem cifrada: você extrai o payload e não pode re-assinar sem a chave. Declare isso.
- Imagem **cifrada** (entropia ~8.0 sustentada, sem header reconhecível): pare e reporte — chave ausente é `BLOCKED_BY_EXTERNAL_DEPENDENCY`.

## O que procurar no rootfs extraído (ordem de valor)
| Alvo | Onde | Serve para |
|---|---|---|
| init e serviços | `/etc/init.d/`, `/etc/rc.d/`, `systemd/*.service` | mapa de execução |
| binário do serviço de rede | `/usr/sbin/`, `/usr/bin/` | superfície e protocolo |
| credenciais/segredos | `/etc/passwd`, `/etc/shadow`, `/etc/config`, chaves em `/etc/ssl`, `/root` | achado de segurança (não copie valor) |
| certificados e chaves privadas | `.pem`, `.key`, `server.crt` | confiança embutida |
| config de rede | `/etc/network/*`, `hostapd.conf`, `dhcpd.conf` | comportamento e C2 |
| binário que fala com hardware | strings de `/dev/`, `gpio`, `spi`, `i2c` | ponte para o driver |
| versão e plataforma | `/etc/os-release`, `/etc/banner`, `busybox --help` | casar com kernel/SDK |

## Segurança ao extrair
- **Não** monte imagem em loop no host (um `ext4` malicioso explora o kernel). Use `debugfs`/extração em container.
- **Não** execute script do rootfs no host. Script de firmware roda em qemu com rede off.
- Arquivo extraído pode conter symlink para fora (`../../etc/shadow`) — extraia em container/jail e trate symlink absoluto como achado.

## Registro de extração
```
ORIGEM: <path> sha256=<hash> tamanho=<bytes>
ARTEFATO: <nome> | offset=0x<...> | tamanho=<bytes> | sha256=<hash> | tipo=<...>
FERRAMENTA: binwalk <versão> / unsquashfs <versão>
INTEGRIDADE: CRC/MD5 declarado = <ok|falhou|não declarado>
FALHAS: <extrator ausente | offset incerto | payload cifrado>
```
Cada artefato com offset e hash é o que permite ao próximo analista reproduzir sem refazer a triagem.
