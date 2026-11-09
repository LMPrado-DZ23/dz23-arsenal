# FIRMWARE MAP — <alvo>

> SHA-256 do dump: `<hash>` · tamanho: `<bytes>` · dump verificado por 2 leituras: `<sim/não>`

## Mapa de flash
| Região | Offset | Tamanho | Conteúdo | Proteção |
|---|---|---|---|---|
| bootloader | 0x0 | | U-Boot / ESP bootloader | |
| tabela de partição | 0x8000 | 0xC00 | ESP partition table | |
| app / kernel | 0x10000 | | | |
| rootfs | | | squashfs / UBI / ext4 | dm-verity? |
| config / NVS | | | | |
| recovery / ota | | | | |

## Cadeia de boot
```
ROM → SPL → <bootloader> → <kernel> → <rootfs> → init → serviços
```
| Elo | Artefato | Verificação | Achado |
|---|---|---|---|
| bootloader | | assinatura? | |
| kernel | | hash/FIT? | |
| rootfs | | verity? | |
| serviços | | | |

## Rootfs extraído
| Caminho | Papel | Analisar depois? |
|---|---|---|
| `/etc/init.d/*` | serviços | |
| `/usr/sbin/<x>` | binário de rede | |
| `/etc/config` | configuração | |
| `/etc/passwd`, `/etc/shadow` | credenciais | achado, sem expor valor |

## Interfaces físicas (só com autorização)
| Interface | Presente | Autorização | Observação |
|---|---|---|---|
| UART | | | tensão: |
| JTAG/SWD | | | |
| SPI/I2C | | | |

## Riscos
- **Brick**: <o que pode inutilizar o aparelho>
- **Secure boot/OTP**: <se existe>
- **Cifra**: <se existe — entropia medida>

## Não analisado
- <região/binário> — motivo: <cifrado | ferramenta | escopo>
