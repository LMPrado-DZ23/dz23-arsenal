# Boot, hardware e risco físico

## Regra
Ler firmware é seguro; **tocar no dispositivo não é**. Toda ação que escreve em flash, altera fusível, alimenta pino ou abre o aparelho exige autorização explícita, backup do dump original e plano de recuperação.

## Cadeia de boot (onde a análise começa)
```
ROM/bootloader → SPL → U-Boot → kernel (zImage/uImage/FIT) → initramfs/rootfs → init → serviços
```
Cada elo tem assinatura própria; um secure boot ativo significa que a etapa anterior **verifica** a seguinte.

| Elo | O que examinar | Sinal de proteção |
|---|---|---|
| ROM | não acessível (OTP) | — |
| SPL/U-Boot | `u-boot.bin`, `bootcmd`, `bootargs` | `CONFIG_FIT_SIGNATURE`, verified boot |
| Kernel | `zImage`/`Image`/uImage | módulo assinado, `CONFIG_MODULE_SIG_FORCE` |
| Rootfs | squashfs/UBI/ext4 | dm-verity (hash tree no fim da partição) |
| Serviços | init scripts | watchdog, rollback A/B |

`bootargs` no U-Boot é a fonte mais rica: console, rootfs, MAC, partição de recuperação.

## Interfaces físicas (somente com autorização)
| Interface | Uso | Risco |
|---|---|---|
| **UART** | console de boot, shell | baixo (leitura); cuidado com tensão |
| **JTAG/SWD** | debug, dump de memória, bypass de boot | médio — pode travar CPU |
| **SPI/I2C (clip)** | dump de flash NOR/NAND | médio — leitura com alimentação errada corrompe |
| **eMMC via adaptador** | dump completo | baixo se feito fora da placa |
| **USB DFU/BootROM** | dump/restore | alto — modo pode apagar região |

Regras de bancada: confirme **tensão** (1.8 V vs 3.3 V) antes de conectar; nunca alimente o chip e a placa ao mesmo tempo; leia duas vezes e compare hash antes de considerar o dump válido (`dump1.sha == dump2.sha`).

## Dump: validação antes de analisar
```bash
sha256sum dump1.bin dump2.bin          # precisam ser iguais
file dump1.bin && xxd -l 64 dump1.bin
# regiões de 0x00 ou 0xFF sustentadas = leitura falha ou área apagada
python -c "d=open('dump1.bin','rb').read(); import collections; c=collections.Counter(d[:65536]); print(c.most_common(3))"
```
Dump com bloco inteiro de `0xFF` é flash apagada; bloco de `0x00` é leitura falha. **Não** analise como se fosse conteúdo.

## Escrita em dispositivo (só com autorização + backup)
1. Dump completo e **verificado por hash** (duas leituras).
2. Backup fora do dispositivo, em dois lugares.
3. Confirmar mapa de partição e offset de destino (`0x0` errado = brick).
4. Ter plano de recuperação (bootloader de serviço, DFU, clip SPI).
5. Registrar comando exato e versão da ferramenta.
Sem 1–5, a resposta é `BLOCKED_BY_EXTERNAL_DEPENDENCY` ou `NEEDS_APPROVAL` — nunca "tenta e vê".

## Firmware assinado vs cifrado
- **Assinado**: você extrai e lê; não consegue regravar sem a chave (o bootloader rejeita). Analisar é possível; modificar não.
- **Cifrado**: sem a chave, o payload é ruído (entropia ~8.0). Declare e pare.
- **Secure boot com OTP**: mesmo com a chave, o fusível pode impedir qualquer imagem não oficial — a modificação é irreversível.

## Legal e ético (não é formalidade)
- Você precisa de **direito**: ser dono do dispositivo, ter contrato de pesquisa, licença que permita, ou autorização escrita.
- Não burle proteção de terceiros sem base legal; não distribua firmware proprietário; não exponha credencial encontrada.
- Achado de segurança deve ser reportado ao fabricante (responsible disclosure), não publicado com PoC pronto.

## Saída
Cadeia de boot mapeada com proteções identificadas, interfaces disponíveis (e a autorização para usá-las), integridade do dump (hash duplo), e a lista do que **não** foi feito por falta de autorização/risco.
