# Emulação de firmware

## Por que emular
Ver o firmware **rodando** revela init, serviços, protocolo e portas — sem comprar o hardware. Mas emulação de firmware é aproximação: periférico ausente **não** é bug do firmware.

## Escolha do modo
| Modo | Quando | Comando |
|---|---|---|
| **qemu-user** | um binário só (MIPS/ARM estático) | `qemu-mipsel -L ./rootfs ./rootfs/usr/sbin/servico` |
| **qemu-system** | imagem completa, com kernel | `qemu-system-arm -M virt -kernel zImage -drive file=rootfs.img,format=raw` |
| **FirmAE/firmadyne-like** | automação de várias imagens | script de rede/injetação de NVRAM |
| **unicórnio/emulação parcial** | só uma função (cripto, checksum) | Unicorn/`angr` com mapa de memória |

qemu-user é o caminho mais rápido e o que mais falha por falta de `libc` — resolva com `-L` apontando para o rootfs extraído.

## qemu-user: roteiro
```bash
# descobrir a arch real antes
readelf -h ./rootfs/usr/sbin/servico | grep Machine
# rodar com rootfs como sysroot
qemu-arm -L ./rootfs ./rootfs/usr/sbin/servico --help
# syscalls para ver o que ele espera do ambiente
qemu-arm -strace -L ./rootfs ./rootfs/usr/sbin/servico 2>&1 | head -40
```
`ENOENT` em `/dev/gpio` ou `/proc/...` é sinal de dependência de hardware — registre, não "conserte" o firmware.

## qemu-system: roteiro mínimo
```bash
qemu-system-arm -M versatilepb -m 256M \
  -kernel rootfs/boot/zImage \
  -dtb rootfs/boot/board.dtb \
  -drive file=rootfs.img,format=raw,if=virtio \
  -append "root=/dev/vda rw console=ttyAMA0" \
  -nographic -netdev user,id=n0 -device virtio-net,netdev=n0
```
- `-M` precisa casar com o SoC do devicetree (`compatible` do nó raiz). Ver `references/firmware-formats.md`.
- Sem `-dtb`, o kernel pode não achar UART/flash — sintoma: boot silencioso.
- **Rede em `user` mode** isola do host; sem `-net tap` você não expõe o firmware à rede local.

## Isolar o resto
```bash
# dentro de container, sem rede externa, com a imagem read-only
docker run --rm -it --network=none --cap-drop=ALL -v "$PWD:/fw:ro" debian:trixie-slim bash
```
Confirme com `ip a` (só loopback) e com uma tentativa de `curl` falhando. Isso é a **prova** de isolamento que o relatório exige.

## Depois do boot
| Alvo | Comando | Achado |
|---|---|---|
| init rodou? | `dmesg \| tail`, `ps` | serviços vivos |
| portas abertas | `netstat -lntp` / `ss -lntp` | superfície de rede |
| binário do serviço | `ls -l /proc/<pid>/exe` | qual binário analisar depois |
| config usada | `cat /proc/<pid>/cmdline`, `/etc/config` | parâmetros reais |
| credenciais padrão | `/etc/passwd`, banner | risco (sem expor valor) |
| tráfego | `tcpdump -i lo` no guest | protocolo |

## Limites que precisam entrar no relatório
- **Periférico ausente**: SPI/I2C/GPIO não existem em qemu → função retorna erro → não é falha do firmware.
- **NVRAM/config de fábrica**: muitos firmwares leem variável de bootloader; sem ela, o serviço não sobe.
- **Tempo**: watchdog e timeouts podem reiniciar antes de você observar.
- **Arquitetura parcial**: qemu pode não implementar instrução específica do SoC → `SIGILL` (declare).
- **Anti-emulação**: checagem de `cpuid`/`mrs`/devicetree pode abortar o boot — identifique e registre, sem classificar como malware.

## Quando emular não vale a pena
Firmware de rádio/PHY, DSP, FPGA bitstream, secure boot com chave em OTP: a emulação diz pouco. Nesses casos, o caminho é análise estática + observação de hardware (JTAG/UART com autorização).

## Saída
Modo de emulação, comando exato, evidência de isolamento, o que subiu, o que não subiu **e por quê** (periférico/NVRAM/anti-emulação), e as portas/processos observados.
